import json
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# -------------------------------
# ENVIRONMENT
# -------------------------------
load_dotenv()
llm = ChatOpenAI(model="openai/gpt-4o-mini", temperature=0)

# -------------------------------
# LOCAL DATABASE
# -------------------------------
LOCAL_DB = {
    "fees_2026": {
        "48_pages": {
            "5_years":{"regular":4025,"express":6325,"super_express":8625},
            "10_years":{"regular":5750,"express":8050,"super_express":10350}
        },
        "64_pages": {
            "5_years":{"regular":6325,"express":8625,"super_express":12075},
            "10_years":{"regular":8050,"express":10350,"super_express":13800}
        }
    },
    "required_docs": {
        "adult":["NID","Application Summary","Payment Slip"],
        "minor_under_18":["Birth Registration (English)","Parents NID","3R Photo"],
        "government_staff":["NOC (No Objection Certificate)","NID"]
    }
}

# -------------------------------
# RUN MULTI-AGENT PASSPORT SYSTEM
# -------------------------------
def run_passport_agents(user_input: str) -> str:

    # -------- Greeting Agent --------
    greet_agent = Agent(
        role="Greeting Agent",
        goal="Respond politely to salutations",
        backstory="Friendly virtual consular",
        llm=llm,
        verbose=False
    )
    t_greet = Task(
        description=f"""
User said: "{user_input}"
- If greeting (hi/hello/hey) respond politely
- Else return 'NOT_GREETING'
""",
        agent=greet_agent,
        expected_output="text"
    )

    # -------- Parser Agent --------
    parser_agent = Agent(
        role="Parser Agent",
        goal="Extract structured passport info",
        backstory="Extract age, profession, pages, delivery, has_nid",
        llm=llm,
        verbose=False
    )
    t_parser = Task(
        description=f"""
Extract structured JSON from user input:
"{user_input}"
Return strictly JSON with fields: age, profession, pages, delivery, has_nid
""",
        agent=parser_agent,
        expected_output="json"
    )

    # -------- Detail Agent --------
    detail_agent = Agent(
        role="Detail Agent",
        goal="Ask politely only for missing passport info",
        backstory="Friendly MAS helper",
        llm=llm,
        verbose=False
    )
    t_detail = Task(
        description=f"""
User said: "{user_input}"
Check structured data: {{t_parser.output}}
- Ask politely only for missing fields: age, profession, pages, delivery, has_nid
- If all fields present, respond with 'DETAILS_OK'
""",
        agent=detail_agent,
        expected_output="text",
        context=[t_parser]
    )

    # -------- Policy Agent --------
    policy_agent = Agent(
        role="Policy Guardian",
        goal="Determine passport validity and flag inconsistencies",
        backstory="Bangladesh Passport Policy Expert",
        llm=llm,
        verbose=False
    )
    t_policy = Task(
        description=f"""
Data: {{t_parser.output}}
Rules:
- Under 18 → 5 years only
- 18-65 → use requested 5 or 10 years if provided; else default 10 years
- Over 65 → 5 years only
If requested validity invalid, append ⚠️ warning
Return strictly: Validity: <5 Years or 10 Years> (with ⚠️ if invalid)
""",
        agent=policy_agent,
        expected_output="text",
        context=[t_parser]
    )

    # -------- Fee Agent --------
    fee_agent = Agent(
        role="Fee Calculator",
        goal="Calculate exact BDT fee including 15% VAT using 2026 fee table",
        backstory="Government financial auditor",
        llm=llm,
        verbose=False
    )
    t_fee = Task(
        description=f"""
Applicant Data: {{t_parser.output}}
Policy Decision: {{t_policy.output}}
Use official 2026 fees: {json.dumps(LOCAL_DB['fees_2026'], indent=2)}

- Calculate Total Fee = Base Fee + 15% VAT
- Return strictly:
Delivery Type: <regular/express/super_express>
Total Fee: <amount> BDT
""",
        agent=fee_agent,
        expected_output="text",
        context=[t_parser, t_policy]
    )

    # -------- Document Checklist Agent --------
    docs_agent = Agent(
        role="Document Architect",
        goal="Generate customized document checklist",
        backstory="Documentation specialist",
        llm=llm,
        verbose=False
    )
    t_docs = Task(
        description=f"""
Data: {{t_parser.output}}
Use docs database: {json.dumps(LOCAL_DB['required_docs'])}
Return strictly:
Documents Needed: <comma separated list>
""",
        agent=docs_agent,
        expected_output="text",
        context=[t_parser, t_policy]
    )

    # -------- Crew Execution --------
    crew = Crew(
        agents=[greet_agent, parser_agent, detail_agent, policy_agent, fee_agent, docs_agent],
        tasks=[t_greet, t_parser, t_detail, t_policy, t_fee, t_docs],
        verbose=False
    )
    crew.kickoff()

    # -------- Handle greeting / missing details --------
    greet_reply = str(t_greet.output).strip()
    if greet_reply != "NOT_GREETING":
        return greet_reply

    detail_reply = str(t_detail.output).strip()
    if detail_reply != "DETAILS_OK":
        return detail_reply

    # -------- Extract outputs --------
    validity = str(t_policy.output).strip()
    fee_output = str(t_fee.output).strip()
    docs_output = str(t_docs.output).strip()

    delivery = next((l.split(":")[-1].strip() for l in fee_output.splitlines() if "Delivery" in l), None)
    total_fee = next((l.split(":")[-1].strip() for l in fee_output.splitlines() if "Total Fee" in l), None)

    if not delivery or not total_fee:
        raise ValueError("Agent did not return Delivery or Total Fee. Check agent outputs!")

    readiness = "Not Ready" if "⚠️" in validity else "Ready"

    # -------- Final Report --------
    final_report = f"""
🛂 Passport Readiness Report
==============================
| Field             | Value |
|-------------------|-------|
| Validity          | {validity} |
| Delivery Type     | {delivery} |
| Total Fee         | {total_fee} |
| Documents Needed  | {docs_output.replace('Documents Needed:','').strip()} |
 Readiness: {readiness}
"""
    return final_report.strip()


while True:
    user_text = input("You: ").strip()
    if user_text.lower() in ["exit", "quit"]:
        print("Exiting Bangladesh Virtual Consular")
        break  
    reply = run_passport_agents(user_text)
    print(reply)