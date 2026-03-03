# Bangladesh Virtual Passport MAS

**Bangladesh Virtual Passport MAS** is a cutting-edge **Multi-Agent System (MAS)** developed to assist passport applicants in Bangladesh. Acting as a professional Virtual Consular Officer, it guides users seamlessly through the passport application process, ensures compliance with government policies, calculates fees accurately, and generates a personalized document checklist.

## Key Features

* **Intelligent Greeting Recognition:** Detects and responds to user salutations (`hi`, `hello`, `hey`) politely and professionally.
* **Smart Input Parsing:** Automatically extracts essential applicant details including age, profession, passport pages, delivery type, and NID status from natural language input.
* **Dynamic Detail Verification:** Identifies missing information and prompts users politely to ensure all required data is captured.
* **Policy Compliance & Validation:** Enforces Bangladesh passport rules:

  * Applicants under 18 → 5-year validity only
  * Applicants aged 18–65 → 5 or 10-year validity
  * Applicants over 65 → 5-year validity only
  * Invalid requests are flagged with ⚠️ warnings
* **Accurate Fee Calculation:** Calculates total fees including **15% VAT** based on the official 2026 fee schedule.
* **Personalized Document Checklist:** Generates a customized list of required documents tailored to the applicant’s profile.
* **Comprehensive Passport Readiness Report:** Presents validity, delivery type, total fees, required documents, and readiness status in a clear, professional format.

## Installation

1. Clone the repository:

```bash
https://github.com/codebysajed/virtual-passport-assistant.git
cd virtual-passport-assistant
```

2. Install dependencies (Python 3.10+ recommended) via `requirements.txt`:

```bash
pip install -r requirements.txt
```

3. Configure your OpenAI API key in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

Run the CLI script:

```bash
python main.py
```

### Example Interaction

```text
You: Hi
Virtual Consular: Hello! Welcome to Bangladesh Virtual Passport MAS. How can I assist you today?

You: I am a 24-year-old private sector employee. I need a 64-page passport urgently and I have my NID.
🛂 Passport Readiness Report
==============================
| Field             | Value |
|-------------------|-------|
| Validity          | 10 Years |
| Delivery Type     | super_express |
| Total Fee         | 13800 BDT |
| Documents Needed  | NID, Application Summary, Payment Slip |
 Readiness: Ready

You: quit
👋 Exiting Bangladesh Virtual Consular. Goodbye!
```

## Project Structure

```text
bangladesh-virtual-passport/
│
├─ main.py             # Core MAS implementation
├─ .env                # OpenAI API key configuration
├─ README.md           # Project documentation
└─ requirements.txt    # Python dependencies
```

## Requirements

Create a `requirements.txt` file with the following content:

```
crewai
langchain_openai
python-dotenv
```

## Notes

* Fee calculation is **deterministic and accurate**, using official 2026 rates including VAT.
* The MAS prompts only for missing information, ensuring a smooth and professional user experience.
* ⚠️ Warnings indicate any policy inconsistencies that may affect passport readiness.
