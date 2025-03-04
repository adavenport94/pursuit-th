# Path to trained model
MODEL_PATH = "model.pkl"

# Path to DuckDB file
DB_FILE = "scraper.duckdb"

# Not being used, thought about creating a partition
PARQUET_FILE = "partitioned_links.parquet"

# Threshold used to perform a consecutive scrape on high ranking links
HIGH_SCORE_THRESHOLD = 0.90

# Reinforce by 1.2
PRIORITY_MULTIPLIER = 1.2

# Penalize by .95
NON_PRIORITY_MULTIPLIER = .95

# High-value keywords that indicate strong relevance
PRIORITY_KEY_WORDS = [
    "Budget",
    "Finance",
    "ACFR",
    "Finance Director",
    "Comprehensive Annual Financial Report",
    "Financial Statements",
    "Annual Budget",
    "Expenditure Report",
    "Revenue Summary",
    "Audit Report",
    "Fiscal Year",
    "Budget Allocation",
    "General Fund",
    "Financial Planning",
    "Debt Service",
    "Operating Budget",
    "Capital Improvement Plan",
    "Statement of Net Position",
    "Balance Sheet",
    "Cash Flow Statement",
    "General Ledger",
    "Financial Analysis",
    "Expenditure Forecast",
    "Investment Portfolio",
    "Pension Liabilities",
    "Bond Ratings",
    "Restricted Funds",
    "Unrestricted Funds",
    "Fund Balance",
    "Reserve Fund",
    "Grants & Allocations",
    "State Appropriations",
    "Federal Funding",
    "Municipal Bonds",
    "Tax Revenue",
    "Public Expenditure",
    "Legislative Budget Office",
    "Budget Resolution",
    "Fiscal Responsibility",
    "Debt Management",
    "Government Accountability Office",
    "Generally Accepted Accounting Principles",
    "Governmental Accounting Standards Board",
    "Office of Management and Budget",
    "Single Audit",
    "Transparency Report",
    "Procurement Policy",
    "Public Financial Management",
    "Chief Financial Officer",
    "CFO",
    "Finance Department",
    "Finance Office",
    "Accounting Department",
    "Treasurer",
    "City Treasurer",
    "County Treasurer",
    "Budget Coordinator",
    "Budget Manager",
    "Finance Manager",
    "Financial Controller",
    "Accounts Payable",
    "Accounts Receivable",
    "Audit Committee",
    "Fiscal Officer",
    "Fiscal Services",
    "Treasury Division",
    "Finance Administrator",
    "Director of Budget",
    "Revenue Officer",
    "Financial Services Department",
    "Business Office",
    "Procurement Officer",
    "Grants Manager",
    "Public Finance Director",
    "Financial Compliance",
    "Financial Analyst",
    "Municipal Finance Director",
    "Assistant Finance Director",
    "Finance and Administration",
    "Controller",
    "Senior Accountant",
    "Budget Analyst",
    "Finance Contact",
    "Financial Operations",
    "Public Finance Contact",
    "Treasury Contact",
    "Finance Email",
    "Finance Phone Number",
    "Finance Help Desk",
    "Financial Assistance Contact",
    "Accounts Department Contact",
]

# Low-value keywords that indicate low relevance
NON_PRIORITY_KEY_WORDS = [
    "service request",
    "apply",
    "cancel",
    "customer support",
    "billing",
    "utility",
    "utilities",
    "register",
    "skip",
    "skip to",
    "tickets",
    "request",
]
