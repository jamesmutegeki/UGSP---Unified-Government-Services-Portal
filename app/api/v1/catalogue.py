from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/catalogue", tags=["catalogue"])

SERVICES = [
    # --- Citizen ---
    {"id": 1, "name": "National ID Application", "description": "Apply for a new Ndaga Muntu National ID card or request a replacement.", "ministry": "NIRA", "category": "citizen", "fee": 50000, "turnaround_days": 14, "icon": "badge", "requirements": ["Birth Certificate", "Parent NIN", "Passport Photo"], "active": True},
    {"id": 2, "name": "Passport Application", "description": "Apply for a new Ugandan passport or renew an expiring one.", "ministry": "Ministry of Internal Affairs", "category": "citizen", "fee": 250000, "turnaround_days": 10, "icon": "passport", "requirements": ["National ID", "Passport Photo", "Birth Certificate"], "active": True},
    {"id": 5, "name": "Driving Permit", "description": "Apply for a new driving permit, renew, or upgrade to a different class.", "ministry": "Ministry of Works & Transport", "category": "citizen", "fee": 180000, "turnaround_days": 7, "icon": "directions_car", "requirements": ["National ID", "Passport Photo", "Medical Report"], "active": True},
    {"id": 8, "name": "Marriage Certificate", "description": "Apply for a certified copy of a marriage certificate registered in Uganda.", "ministry": "Ministry of Justice", "category": "citizen", "fee": 75000, "turnaround_days": 7, "icon": "favorite", "requirements": ["National IDs", "Marriage Date", "Place of Marriage"], "active": True},
    {"id": 10, "name": "Birth Certificate", "description": "Register a new birth or request a certified copy.", "ministry": "NIRA", "category": "citizen", "fee": 30000, "turnaround_days": 3, "icon": "child_care", "requirements": ["Parent NIN", "Hospital Notification", "Parent IDs"], "active": True},
    {"id": 12, "name": "Police Clearance Certificate", "description": "Certificate of Good Conduct from Uganda Police Force.", "ministry": "Uganda Police Force", "category": "citizen", "fee": 55000, "turnaround_days": 10, "icon": "verified_user", "requirements": ["National ID", "Passport Photo", "Fingerprint Form"], "active": True},
    {"id": 13, "name": "Voter Registration", "description": "Register to vote or update your voter details with the Electoral Commission.", "ministry": "Electoral Commission", "category": "citizen", "fee": 0, "turnaround_days": 5, "icon": "how_to_vote", "requirements": ["National ID", "Proof of Residence"], "active": True},
    {"id": 14, "name": "Social Security Registration", "description": "Register with NSSF as a member and check your savings.", "ministry": "NSSF", "category": "citizen", "fee": 0, "turnaround_days": 3, "icon": "savings", "requirements": ["National ID", "Employer NSSF Number"], "active": True},
    # --- Business ---
    {"id": 3, "name": "Business Registration", "description": "Register a new business and obtain a Certificate of Incorporation.", "ministry": "URSB", "category": "business", "fee": 150000, "turnaround_days": 5, "icon": "business", "requirements": ["Proposed Name", "Director NINs", "Memorandum of Association"], "active": True},
    {"id": 4, "name": "Tax Registration (TIN)", "description": "Register for a Tax Identification Number with URA.", "ministry": "URA", "category": "business", "fee": 0, "turnaround_days": 1, "icon": "receipt", "requirements": ["National ID", "Proof of Address"], "active": True},
    {"id": 7, "name": "Land Title Search", "description": "Conduct a search on any registered land title to verify ownership.", "ministry": "Ministry of Lands", "category": "business", "fee": 20000, "turnaround_days": 3, "icon": "real_estate_agent", "requirements": ["Title Reference Number", "Owner NIN"], "active": True},
    {"id": 11, "name": "Trading Licence", "description": "Apply for or renew a trading licence for your business.", "ministry": "Local Government", "category": "business", "fee": 120000, "turnaround_days": 7, "icon": "store", "requirements": ["Business Registration", "TIN", "Tax Clearance"], "active": True},
    {"id": 15, "name": "NHIF Registration", "description": "Register employees with the National Health Insurance Scheme.", "ministry": "Ministry of Health", "category": "health", "fee": 50000, "turnaround_days": 5, "icon": "local_hospital", "requirements": ["Company Registration", "Employee List", "TIN"], "active": True},
    {"id": 16, "name": "NEMA Environmental Permit", "description": "Apply for an environmental impact assessment permit for your project.", "ministry": "NEMA", "category": "environmental", "fee": 300000, "turnaround_days": 21, "icon": "forest", "requirements": ["Project Proposal", "EIA Report", "Company Reg"], "active": True},
    # --- Visitor ---
    {"id": 6, "name": "Visa Application", "description": "Apply for a Ugandan visa online — tourist, business, transit, or student.", "ministry": "Ministry of Internal Affairs", "category": "visitor", "fee": 100000, "turnaround_days": 5, "icon": "flight", "requirements": ["Passport", "Passport Photo", "Travel Itinerary"], "active": True},
    {"id": 9, "name": "Work Permit", "description": "Work permit for foreign nationals employed in Uganda.", "ministry": "Ministry of Internal Affairs", "category": "visitor", "fee": 500000, "turnaround_days": 14, "icon": "work", "requirements": ["Passport", "Employment Contract", "Academic Credentials"], "active": True},
    {"id": 17, "name": "Certificate of Residence", "description": "Apply for or renew a Certificate of Residence for foreign residents.", "ministry": "Ministry of Internal Affairs", "category": "visitor", "fee": 200000, "turnaround_days": 7, "icon": "home", "requirements": ["Passport", "Visa", "Proof of Address"], "active": True},
    # --- Health ---
    {"id": 18, "name": "Health Facility Locator", "description": "Find public health facilities near you — hospitals, clinics, and HC IVs.", "ministry": "Ministry of Health", "category": "health", "fee": 0, "turnaround_days": 0, "icon": "local_hospital", "requirements": [], "active": True},
    {"id": 19, "name": "Vaccination Appointment", "description": "Schedule a vaccination appointment at your nearest health centre.", "ministry": "Ministry of Health", "category": "health", "fee": 0, "turnaround_days": 1, "icon": "vaccines", "requirements": ["National ID"], "active": True},
    {"id": 20, "name": "Medical Report Request", "description": "Request copies of medical records from public hospitals.", "ministry": "Ministry of Health", "category": "health", "fee": 15000, "turnaround_days": 5, "icon": "assignment", "requirements": ["National ID", "Hospital Number"], "active": True},
    # --- Education ---
    {"id": 21, "name": "PLE Results Access", "description": "Access Primary Leaving Examination results online.", "ministry": "Ministry of Education", "category": "education", "fee": 0, "turnaround_days": 1, "icon": "school", "requirements": ["Index Number", "Year"], "active": True},
    {"id": 22, "name": "Student Loan Application", "description": "Apply for a tertiary education loan from the Higher Education Students Financing Board.", "ministry": "Ministry of Education", "category": "education", "fee": 0, "turnaround_days": 30, "icon": "account_balance", "requirements": ["National ID", "Admission Letter", "Parent NIN"], "active": True},
    {"id": 23, "name": "School Registration", "description": "Register a new private school or early childhood development centre.", "ministry": "Ministry of Education", "category": "education", "fee": 100000, "turnaround_days": 14, "icon": "kindergarten", "requirements": ["Business Registration", "Premises Report", "Curriculum"], "active": True},
    # --- Financial ---
    {"id": 24, "name": "Tax Filing (E-Return)", "description": "File your annual income tax return electronically with URA.", "ministry": "URA", "category": "financial", "fee": 0, "turnaround_days": 1, "icon": "description", "requirements": ["TIN", "Income Statement"], "active": True},
    {"id": 25, "name": "Business Loan Application", "description": "Apply for a small business loan through the Microfinance Support Centre.", "ministry": "Ministry of Finance", "category": "financial", "fee": 25000, "turnaround_days": 21, "icon": "paid", "requirements": ["Business Registration", "Business Plan", "Tax Clearance"], "active": True},
    {"id": 26, "name": "NSSF Withdrawal", "description": "Apply for NSSF benefits withdrawal upon retirement or qualifying event.", "ministry": "NSSF", "category": "financial", "fee": 0, "turnaround_days": 10, "icon": "account_balance_wallet", "requirements": ["National ID", "NSSF Number", "Bank Details"], "active": True},
    # --- Environmental ---
    {"id": 27, "name": "Tree Planting Permit", "description": "Apply for a permit to plant trees on government land.", "ministry": "NFA", "category": "environmental", "fee": 50000, "turnaround_days": 7, "icon": "park", "requirements": ["Land Title", "Species Plan"], "active": True},
    {"id": 28, "name": "Noise Emission Permit", "description": "Apply for a permit for noise-emitting activities in urban areas.", "ministry": "NEMA", "category": "environmental", "fee": 75000, "turnaround_days": 5, "icon": "volume_up", "requirements": ["Company Registration", "Site Plan"], "active": True},
    {"id": 29, "name": "Water Use Permit", "description": "Apply for a permit to abstract or use water resources.", "ministry": "Ministry of Water", "category": "environmental", "fee": 150000, "turnaround_days": 14, "icon": "water_drop", "requirements": ["Project Description", "EIA Report"], "active": True},
]

MINISTRIES = [
    {"id": 1, "name": "NIRA", "full_name": "National Identification and Registration Authority", "website": "https://www.nira.go.ug", "category": "agency"},
    {"id": 2, "name": "Ministry of Internal Affairs", "full_name": "Ministry of Internal Affairs", "website": "https://www.mia.go.ug", "category": "ministry"},
    {"id": 3, "name": "URSB", "full_name": "Uganda Registration Services Bureau", "website": "https://ursb.go.ug", "category": "agency"},
    {"id": 4, "name": "URA", "full_name": "Uganda Revenue Authority", "website": "https://www.ura.go.ug", "category": "authority"},
    {"id": 5, "name": "Ministry of Works & Transport", "full_name": "Ministry of Works and Transport", "website": "https://www.works.go.ug", "category": "ministry"},
    {"id": 6, "name": "Ministry of Lands", "full_name": "Ministry of Lands, Housing and Urban Development", "website": "https://www.mlhud.go.ug", "category": "ministry"},
    {"id": 7, "name": "Ministry of Justice", "full_name": "Ministry of Justice and Constitutional Affairs", "website": "https://www.justice.go.ug", "category": "ministry"},
    {"id": 8, "name": "Ministry of Health", "full_name": "Ministry of Health", "website": "https://www.health.go.ug", "category": "ministry"},
    {"id": 9, "name": "Ministry of Education", "full_name": "Ministry of Education and Sports", "website": "https://www.education.go.ug", "category": "ministry"},
    {"id": 10, "name": "Ministry of Finance", "full_name": "Ministry of Finance, Planning and Economic Development", "website": "https://www.finance.go.ug", "category": "ministry"},
    {"id": 11, "name": "Ministry of Water", "full_name": "Ministry of Water and Environment", "website": "https://www.mwe.go.ug", "category": "ministry"},
    {"id": 12, "name": "Ministry of Agriculture", "full_name": "Ministry of Agriculture, Animal Industry and Fisheries", "website": "https://www.agriculture.go.ug", "category": "ministry"},
    {"id": 13, "name": "Ministry of ICT", "full_name": "Ministry of ICT and National Guidance", "website": "https://www.ict.go.ug", "category": "ministry"},
    {"id": 14, "name": "NEMA", "full_name": "National Environment Management Authority", "website": "https://www.nema.go.ug", "category": "authority"},
    {"id": 15, "name": "NFA", "full_name": "National Forestry Authority", "website": "https://www.nfa.go.ug", "category": "authority"},
    {"id": 16, "name": "NSSF", "full_name": "National Social Security Fund", "website": "https://www.nssf.go.ug", "category": "fund"},
    {"id": 17, "name": "Electoral Commission", "full_name": "Electoral Commission of Uganda", "website": "https://www.ec.or.ug", "category": "commission"},
    {"id": 18, "name": "Uganda Police Force", "full_name": "Uganda Police Force", "website": "https://www.upf.go.ug", "category": "security"},
    {"id": 19, "name": "Local Government", "full_name": "Ministry of Local Government", "website": "https://www.molg.go.ug", "category": "ministry"},
    {"id": 20, "name": "UBOS", "full_name": "Uganda Bureau of Statistics", "website": "https://www.ubos.org", "category": "agency"},
    {"id": 21, "name": "UNBS", "full_name": "Uganda National Bureau of Standards", "website": "https://www.unbs.go.ug", "category": "agency"},
    {"id": 22, "name": "NITA-U", "full_name": "National Information Technology Authority-Uganda", "website": "https://www.nita.go.ug", "category": "authority"},
    {"id": 23, "name": "UCC", "full_name": "Uganda Communications Commission", "website": "https://www.ucc.co.ug", "category": "commission"},
    {"id": 24, "name": "Ministry of Energy", "full_name": "Ministry of Energy and Mineral Development", "website": "https://www.energy.go.ug", "category": "ministry"},
    {"id": 25, "name": "Ministry of Tourism", "full_name": "Ministry of Tourism, Wildlife and Antiquities", "website": "https://www.tourism.go.ug", "category": "ministry"},
]


@router.get("")
async def list_services(category: str = Query(None)):
    if category:
        return [s for s in SERVICES if s["category"] == category and s["active"]]
    return [s for s in SERVICES if s["active"]]


@router.get("/search")
async def search_services(q: str = Query("")):
    if not q:
        return []
    q = q.lower()
    return [s for s in SERVICES if s["active"] and (q in s["name"].lower() or q in s["ministry"].lower() or q in s["description"].lower())]


@router.get("/ministries")
async def list_ministries():
    return MINISTRIES


@router.get("/ministries/search")
async def search_ministries(q: str = Query("")):
    if not q:
        return MINISTRIES
    q = q.lower()
    return [m for m in MINISTRIES if q in m["name"].lower() or q in m["full_name"].lower()]


@router.get("/{service_id}")
async def get_service(service_id: int):
    for s in SERVICES:
        if s["id"] == service_id and s["active"]:
            return s
    raise HTTPException(status_code=404, detail="Service not found")
