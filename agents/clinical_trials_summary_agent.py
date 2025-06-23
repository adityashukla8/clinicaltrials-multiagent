import os
import logging
import concurrent.futures
from tools.tavily_search import tavily_search
from tools.appwrite_write_trial_info import insert_trial_summary_to_appwrite

from ipdb import set_trace as ipdb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_trial_summary_card(nct_id: str) -> dict:
    queries = {
        "official_title": f"clinical trial: {nct_id} official title site:clinicaltrials.gov/study/{nct_id}",
        "sponsor_info": f"clinical trial: {nct_id} sponsor OR lead investigator site:clinicaltrials.gov/study/{nct_id}",
        "location_and_site_details": f"clinical trial: {nct_id} location hospital site:clinicaltrials.gov/study/{nct_id}",
        "enrollment_info": f"clinical trial: {nct_id} enrollment criteria OR phase OR recruitment status site:clinicaltrials.gov",
        "known_side_effects": f"clinical trial: {nct_id} trial side effects OR adverse events site:pubmed.ncbi.nlm.nih.gov OR site:nature.com",
        "patient_experiences": f"clinical trial: {nct_id} trial experience site:reddit.com OR site:cancerforums.net",
        "external_notes": f"clinical trial: {nct_id} site:mdanderson.org OR site:stanford.edu OR site:nejm.org",
        "objective_summary": f"clinical trial: {nct_id} study objectives OR estimands site:clinicaltrials.gov",
        "dsmc_presence": f"clinical trial: {nct_id} data safety monitoring committee OR DSMB site:clinicaltrials.gov",
        "statistical_plan": f"clinical trial: {nct_id} statistical analysis OR endpoints site:clinicaltrials.gov",
        "sample_size": f"clinical trial: {nct_id} sample size OR number of participants site:clinicaltrials.gov",
        "intervention_arms": f"clinical trial: {nct_id} intervention arms OR comparator site:clinicaltrials.gov",
        "sponsor_contact": f"clinical trial: {nct_id} contact information sponsor or site staff site:clinicaltrials.gov",
        "sites": f"clinical trial: {nct_id} trial site locations OR investigators site:.edu OR site:.org",
        "monitoring_frequency": f"clinical trial: {nct_id} monitoring plan OR MOP frequency site:clinicaltrials.gov",
        "safety_documents": f"clinical trial: {nct_id} adverse event form OR MOP site:nejm.org OR site:pubmed.ncbi.nlm.nih.gov",
        "patient_faq_summary": f"clinical trial: {nct_id} trial patient FAQ or questions site:reddit.com OR site:cancerforums.net",
        "pre_req_for_participation": f"clinical trial: {nct_id} trial required tests OR baseline scans OR eligibility imaging"
    }

    summary_card = {"nct_id": nct_id, "sections": {}}

    def fetch_section(section, query):
        result = tavily_search(query)
        return section, {
            "summary": result["summary"],
            "citations": result["citations"]
        }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_section, s, q): s for s, q in queries.items()}
        for future in concurrent.futures.as_completed(futures):
            section, result = future.result()
            summary_card["sections"][section] = result

        insert_trial_summary_to_appwrite(summary_card)
        logger.info(f"Summary card for {nct_id} inserted into Appwrite")
        # ipdb()

    return summary_card

if __name__ == "__main__":
    nct_id = "NCT05863195"
    summary_card = get_trial_summary_card(nct_id)
    print(summary_card)