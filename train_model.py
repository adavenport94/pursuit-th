import pandas as pd

from url_ranking_model import UrlRanker
from config import MODEL_PATH

# Training Data
data = [
    # Valid URLs - Finance, ACFR, Budget, Financial Reports
    (
        "https://fpb.msu.edu/budget-framework-and-considerations",
        "Budget Framework and Considerations - MSU",
        1,
    ),
    (
        "https://fpb.msu.edu/analysis-and-reporting",
        "Budget Analysis and Reporting - MSU",
        1,
    ),
    (
        "https://www.a2gov.org/finance-and-administrative-services/purchasing/bid-process",
        "City Bids & Contracts - Ann Arbor",
        1,
    ),
    (
        "https://finance.msu.edu/about/meet-the-ed-strategic-projects-initiatives",
        "Meet the Executive Director of Strategic Projects and Initiatives - MSU",
        1,
    ),
    (
        "https://fpb.msu.edu/planning-and-budgeting-overview",
        "Planning and Budgeting Overview",
        1,
    ),
    (
        "https://www.a2gov.org/departments/finance-admin-services/financial-reporting",
        "Financial Reports",
        1,
    ),
    (
        "https://www.a2gov.org/departments/finance-admin-services/purchasing",
        "Purchasing and Contracts",
        1,
    ),
    ("https://www.boerneisd.net/financial-transparency", "Financial Transparency", 1),
    (
        "https://www.boerneisd.net/business-and-financial-services",
        "Business and Financial Services",
        1,
    ),
    ("https://www.bozeman.net/government/finance", "Finance Department", 1),
    (
        "https://www.bozeman.net/government/finance/annual-comprehensive-financial-reports",
        "Annual Comprehensive Financial Reports (ACFR)",
        1,
    ),
    (
        "https://www.sco.ca.gov/Files-ARD/ACFR/acfr22web.pdf",
        "Annual Comprehensive Financial Report",
        1,
    ),
    (
        "https://www.chicago.gov/content/dam/city/depts/fin/supp_info/CAFR/2023CAFR/ACFR_2023.pdf",
        "Annual Comprehensive Financial Report",
        1,
    ),
    (
        "https://www.michigan.gov/budget/-/media/Project/Websites/budget/Fiscal/Spending-and-Revenue-Reports/CAFR/ACFR-FY2022.pdf",
        "Annual Comprehensive Financial Report",
        1,
    ),
    # Valid URLs - Finance-Related Contacts
    (
        "https://fpb.msu.edu/contact",
        "Contact the Office of Financial Planning and Budget - MSU",
        1,
    ),
    (
        "https://detroitmi.gov/Portals/0/docs/Purchasing/Purchasing%20Staff%20Contact%20List%20Effective%201-5-15%20Rev%2012_8_14.pdf",
        "Finance Purchasing Division Staff Contact List",
        1,
    ),
    (
        "https://www.oregon.gov/das/Financial/Acctng/Documents/ACFR_Contacts.pdf",
        "Oregon State Government - ACFR Contacts",
        1,
    ),
    (
        "https://www.losgatosca.gov/DocumentCenter/View/38993/Annual-Comprehensive-Financial-Report-Preparation-Services-RFP",
        "Finance Department Contact",
        1,
    ),
    (
        "https://www.myfloridacfo.com/docs-sf/accounting-and-auditing-libraries/manuals/agencies/annual-comprehensive-financial-report-guidance-document.pdf?sfvrsn=e0ccceb0_8",
        "ACFR Guidance Contact",
        1,
    ),
    (
        "https://hcai.ca.gov/document/siera-snf-acfr-quickstart-guide-series-1-getting-started-in-siera/",
        "California Health Care Access and Information ACFR Support",
        1,
    ),
    (
        "https://finance.umich.edu/contact",
        "University of Michigan Finance Department",
        1,
    ),
    ("https://www.whitehouse.gov/omb/", "Office of Management and Budget (OMB)", 1),
    (
        "https://www.lansingmi.gov/172/Finance-Department",
        "City of Lansing, MI Finance Department",
        1,
    ),
    (
        "https://detroitmi.gov/departments/office-chief-financial-officer/ocfo-divisions",
        "Office of the Chief Financial Officer (OCFO)",
        1,
    ),
    (
        "https://www.myfloridacfo.com/about/meet-the-cfo",
        "Meet the Chief Financial Officer of Florida Jimmy Patronis",
        1,
    ),
    (
        "https://www.myfloridacfo.com/sitePages/contactUs.aspx",
        "Contact Florida CFO Office Jimmy Patronis",
        1,
    ),
    (
        "https://community.pepperdine.edu/finance/chief-financial-officer/",
        "Pepperdine University CFO Greg G. Ramirez",
        1,
    ),
    (
        "https://www.michigan.gov/treasury/contact-us",
        "Michigan Department of Treasury CFO Contact",
        1,
    ),
    (
        "https://detroitmi.gov/departments/office-chief-financial-officer/ocfo-divisions",
        "Detroit Office of the Chief Financial Officer (OCFO)",
        1,
    ),
    (
        "https://www.usa.gov/agencies/chief-financial-officers-council",
        "Chief Financial Officers Council (CFOC) USA.gov",
        1,
    ),
    (
        "https://www.nyc.gov/assets/omb/downloads/pdf/omb_staff.pdf",
        "NYC Office of Management and Budget (OMB) Contact Staff Directory",
        1,
    ),
    (
        "https://www.a2gov.org/finance-and-administrative-services/purchasing/request-for-proposals",
        "Request for Proposals",
        1,
    ),
    (
        "https://www.a2gov.org/finance-and-administrative-services/purchasing/invitation-to-bid",
        "Invitation to Bid",
        1,
    ),
    (
        "https://www.a2gov.org/finance-and-administrative-services/purchasing/bid-process",
        "Bid Process",
        1,
    ),
    (
        "https://www.a2gov.org/finance-and-administrative-services/purchasing/statement-of-qualifications-and-request-for-information",
        "Statement Of Qualifications and Request For Information",
        1,
    ),
    # Invalid URLs - General Contact Pages
    ("https://www.a2gov.org/contact", "Contact Ann Arbor Government", 0),
    ("https://bozeman.net/about/contact", "Contact Bozeman City Officials", 0),
    ("https://asu.edu/contact-directory", "ASU Contact Directory", 0),
    # Invalid URLs - Non-Finance Related
    (
        "https://www.a2gov.org/news/parks-recreation",
        "Ann Arbor Parks & Recreation Updates",
        0,
    ),
    (
        "https://www.a2gov.org/events/music-festival",
        "Upcoming Music Festival in Ann Arbor",
        0,
    ),
    (
        "https://bozeman.net/departments/public-works",
        "Bozeman Public Works Department",
        0,
    ),
    ("https://bozeman.net/departments/library", "Bozeman Public Library Catalog", 0),
    (
        "https://asu.edu/athletics/football-news",
        "Arizona State University Football Scores",
        0,
    ),
    ("https://asu.edu/admissions/how-to-apply", "ASU Admissions Guide", 0),
    (
        "https://boerneisd.net/schools/high-school-sports",
        "Boerne ISD High School Sports",
        0,
    ),
    (
        "https://boerneisd.net/departments/technology-services",
        "Boerne ISD Technology Services",
        0,
    ),
    ("https://www.a2gov.org/news/community-events", "Ann Arbor Community Events", 0),
    ("https://bozeman.net/departments/city-parks", "Bozeman Parks and Recreation", 0),
    ("https://asu.edu/housing/residence-life", "ASU Student Housing Information", 0),
    ("https://boerneisd.net/campus-activities", "Boerne ISD Campus Events", 0),
    ("https://www.a2gov.org/police-department", "Police Department", 0),
    (
        "https://www.a2gov.org/finance-and-administrative-services/assessing/property-tax-and-assessment",
        "Taxes",
        0,
    ),
    ("https://www.facebook.com/TheCityOfAnnArbor", "Facebook", 0),
    ("https://www.instagram.com/thecityofannarborgovernment", "Instagram", 0),
    ("https://www.youtube.com/user/ctnannarbor", "YouTube", 0),
    (
        "https://www.bozeman.net/departments/finance/utilities-services/utility-service-e-notification-request",
        "E-Notification Request",
        0,
    ),
    (
        "https://www.bozeman.net/departments/finance/utilities-services/utility-service-request",
        "SERVICE REQUEST",
        0,
    ),
    (
        "https://www.bozeman.net/departments/finance/utilities-services",
        "Pay Utility Bill",
        0,
    ),
    (
        "https://www.a2gov.org/finance-and-administrative-services/purchasing/bid-process#site-footer",
        "Skip to footer",
        0,
    ),
    (
        "https://www.a2gov.org/finance-and-administrative-services/purchasing/bid-process#site-content",
        "Skip to main content",
        0,
    ),
    # Generated URLs
    (
        "https://www.a2gov.org/departments/finance/ACFR-2024.pdf",
        "Annual Comprehensive Financial Report (ACFR)",
        1,
    ),
    (
        "https://www.a2gov.org/departments/finance/Documents/Budget_2024.pdf",
        "City Budget PDF",
        1,
    ),
    (
        "https://bozeman.net/departments/finance/budget-reports",
        "Bozeman Annual Budget Reports",
        1,
    ),
    ("https://bozeman.net/departments/finance/acfr-reports", "Bozeman ACFR Reports", 1),
    (
        "https://asu.edu/finance/budget-overview",
        "Arizona State University Financial Overview",
        1,
    ),
    ("https://asu.edu/finance/documents/ACFR-2024.pdf", "ASU ACFR 2024 Document", 1),
    (
        "https://boerneisd.net/departments/finance/documents/budget-summary.pdf",
        "Boerne ISD Budget Summary 2024",
        1,
    ),
    (
        "https://boerneisd.net/departments/finance/annual-reports",
        "Annual Financial Reports - Boerne ISD",
        1,
    ),
    (
        "https://www.a2gov.org/departments/finance/Expenditure-Plan-2024.pdf",
        "City Expenditure Plan 2024",
        1,
    ),
    (
        "https://www.a2gov.org/departments/finance/Documents/Fiscal_Report_2024.pdf",
        "Fiscal Report 2024 PDF",
        1,
    ),
    (
        "https://bozeman.net/departments/finance/funding-reports",
        "Bozeman Annual Funding Reports",
        1,
    ),
    (
        "https://bozeman.net/departments/finance/audit-reports",
        "Bozeman Audit Reports",
        1,
    ),
    ("https://asu.edu/finance/spending-plan", "ASU Spending Plan Overview", 1),
    (
        "https://asu.edu/finance/documents/Annual-Financial-Report-2024.pdf",
        "Annual Financial Report (AFR) 2024",
        1,
    ),
    (
        "https://boerneisd.net/departments/finance/documents/municipal-budget-summary.pdf",
        "Municipal Budget Summary 2024",
        1,
    ),
    (
        "https://boerneisd.net/departments/finance/year-end-financial-report",
        "Year-End Financial Report - Boerne ISD",
        1,
    ),
    (
        "https://boerneisd.net/departments/business-and-financial-services/financial-accountability",
        "Financial Accountability",
        1,
    ),
    (
        "https://boerneisd.net/departments/business-and-financial-services/bsac",
        "Budget Strategy and Advisory Committee",
        1,
    ),
    (
        "https://finance.ca.gov/reports/annual-expenditure-report",
        "California Annual Expenditure Report",
        1,
    ),
    (
        "https://treasury.state.tx.us/fiscal-policy/budget-funds",
        "Texas State Treasury Budget & Funds",
        1,
    ),
    (
        "https://chicago.gov/departments/finance/audit-statements",
        "Chicago Financial Audit Statements",
        1,
    ),
    # Generated Invalid
    ("https://www.examplecity.gov/news/local-events", "Upcoming Local Events", 0),
    ("https://www.exampleuniversity.edu/news/student-life", "Student Life News", 0),
    (
        "https://www.examplecounty.org/updates/community-initiatives",
        "Community Initiatives Updates",
        0,
    ),
    ("https://parks.example.gov/trails/hiking", "Hiking Trails and Maps", 0),
    (
        "https://www.examplecity.gov/recreation/summer-camps",
        "Summer Camps Registration",
        0,
    ),
    ("https://www.examplecounty.gov/recreation/sports", "Community Sports Leagues", 0),
    (
        "https://www.examplecounty.gov/departments/public-works/road-maintenance",
        "Road Maintenance and Repairs",
        0,
    ),
    (
        "https://publicworks.examplecity.gov/garbage-recycling",
        "Garbage and Recycling Services",
        0,
    ),
    (
        "https://www.example.gov/departments/transportation/bus-schedules",
        "Public Transportation Bus Schedules",
        0,
    ),
    (
        "https://www.examplegov.org/services/voter-registration",
        "Voter Registration Information",
        0,
    ),
    (
        "https://gov.example.com/departments/dmv/drivers-license",
        "Renew Your Driver’s License",
        0,
    ),
    (
        "https://www.examplecounty.gov/animal-services/adoption",
        "Pet Adoption Services",
        0,
    ),
    (
        "https://university.example.edu/admissions/visit-campus",
        "Schedule a Campus Visit",
        0,
    ),
    (
        "https://www.examplecollege.edu/student-life/dormitory-rules",
        "Student Housing Guidelines",
        0,
    ),
    (
        "https://www.exampleuniversity.edu/departments/computer-science",
        "Computer Science Department",
        0,
    ),
    ("https://www.examplecity.gov/police/report-a-crime", "Report a Crime Online", 0),
    (
        "https://fire.examplecounty.gov/prevention/fire-safety-tips",
        "Fire Safety Tips for Homeowners",
        0,
    ),
    (
        "https://www.examplegov.org/emergency/evacuation-routes",
        "Emergency Evacuation Routes",
        0,
    ),
    ("https://twitter.com/examplegov", "Follow ExampleGov on Twitter", 0),
    (
        "https://www.linkedin.com/company/exampleuniversity",
        "Example University LinkedIn Page",
        0,
    ),
    ("https://www.tiktok.com/@examplecitygov", "Example City Gov TikTok", 0),
    ("https://www.examplegov.org/terms-of-service", "Website Terms of Service", 0),
    (
        "https://www.exampleuniversity.edu/privacy-policy",
        "University Privacy Policy",
        0,
    ),
    ("https://www.examplecity.gov/faq", "Frequently Asked Questions", 0),
    (
        "https://www.examplehealth.org/vaccinations/schedule-appointment",
        "Schedule a COVID-19 Vaccine",
        0,
    ),
    (
        "https://www.examplegov.org/housing-assistance",
        "Affordable Housing Assistance",
        0,
    ),
    (
        "https://www.examplehospital.org/services/urgent-care",
        "Urgent Care Services Near You",
        0,
    ),
    ("https://www.examplecity.gov/site-map", "Site Map", 0),
    ("https://www.examplegov.org/help", "Help and Support Page", 0),
    ("https://examplecity.com/#top", "Skip to Top of Page", 0),
    (
        "https://www.exampleuniversity.edu/athletics/football-budget",
        "University Football Team Budget Overview",
        0,
    ),
    (
        "https://www.examplecitysports.com/youth-league-fundraising",
        "Youth League Fundraising Event",
        0,
    ),
    (
        "https://www.exampleolympics.org/financial-planning-for-athletes",
        "Financial Planning Tips for Olympic Athletes",
        0,
    ),
    (
        "https://www.exampleblog.com/budget-friendly-vacation-tips",
        "Budget-Friendly Travel Tips for Families",
        0,
    ),
    (
        "https://www.examplecreditunion.org/personal-financial-planning",
        "Personal Financial Planning 101",
        0,
    ),
    (
        "https://www.exampletravelagency.com/budget-travel-destinations",
        "Top Budget Travel Destinations",
        0,
    ),
    (
        "https://www.exampletechreview.com/best-financial-planning-apps",
        "Top 10 Financial Planning Apps Reviewed",
        0,
    ),
    (
        "https://www.examplecorporation.com/annual-budget-report",
        "Corporate Budget Report (Internal Document)",
        0,
    ),
    (
        "https://www.examplemarketingagency.com/client-investment-strategies",
        "Marketing Agency: Client Investment Strategies",
        0,
    ),
    (
        "https://www.exampleconsulting.com/small-business-audit",
        "Audit Process for Small Businesses",
        0,
    ),
    (
        "https://www.examplefundraiser.org/annual-budget",
        "Fundraiser Annual Budget Breakdown",
        0,
    ),
    (
        "https://www.examplecharity.com/donation-financial-goals",
        "Nonprofit Financial Goals for Donations",
        0,
    ),
    (
        "https://www.examplegovernance.org/audit-charity-financials",
        "Charity Financial Audit Requirements",
        0,
    ),
    (
        "https://www.exampleinvesting.com/beginner-stock-market-fundamentals",
        "Stock Market Basics for Beginners",
        0,
    ),
    (
        "https://www.examplecrypto.com/blockchain-audit-reports",
        "Audit Reports in Blockchain and Crypto",
        0,
    ),
    (
        "https://www.examplerealestate.com/investment-property-financing",
        "How to Finance Your First Investment Property",
        0,
    ),
    (
        "https://www.exampletech.com/finance-cybersecurity-threats",
        "Cybersecurity Risks in the Finance Industry",
        0,
    ),
    (
        "https://www.exampleai.com/ai-in-financial-sector",
        "The Role of AI in Financial Services",
        0,
    ),
    (
        "https://www.examplecloudservices.com/budgeting-for-cloud-computing",
        "How to Budget for Cloud Computing Services",
        0,
    ),
    (
        "https://www.examplepolitics.com/budget-policy-debate",
        "2024 Budget Policy Debate - Opinions",
        0,
    ),
    (
        "https://www.exampletransparency.org/government-financial-ethics",
        "Government Financial Ethics Investigation",
        0,
    ),
    (
        "https://www.examplewatchdog.com/audit-political-campaign-funding",
        "Audit Report on Political Campaign Funding",
        0,
    ),
    (
        "https://www.examplelawfirm.com/corporate-finance-laws",
        "Corporate Finance Laws & Regulations",
        0,
    ),
    (
        "https://www.examplelegal.org/tax-audit-defense-strategies",
        "How to Defend Yourself in a Tax Audit",
        0,
    ),
    (
        "https://www.exampleprivacywatch.org/financial-data-protection",
        "Consumer Data Protection in Financial Transactions",
        0,
    ),
    (
        "https://www.exampleweddingplanner.com/wedding-budget-guide",
        "Wedding Budget Planning Guide",
        0,
    ),
    (
        "https://www.examplehomeimprovement.com/home-renovation-budget",
        "Budgeting for Home Renovation Projects",
        0,
    ),
    (
        "https://www.examplegaming.com/budget-gaming-pc-builds",
        "Best Budget Gaming PC Builds in 2024",
        0,
    ),
    (
        "https://www.examplefitness.com/nutrition-audit-plan",
        "Personalized Nutrition Audit Plan",
        0,
    ),
    (
        "https://www.exampleeducation.com/audit-your-study-habits",
        "Audit Your Study Habits for Better Learning",
        0,
    ),
    (
        "https://www.exampleseoagency.com/seo-audit-checklist",
        "SEO Audit Checklist for Websites",
        0,
    ),
    (
        "https://www.examplecrowdsourcing.com/how-to-fund-your-creative-project",
        "How to Fund Your Creative Project",
        0,
    ),
    (
        "https://www.examplemusic.com/musicians-fundraising-guide",
        "Fundraising Guide for Independent Musicians",
        0,
    ),
    (
        "https://www.exampleartgallery.com/public-art-funding-strategies",
        "Public Art Funding Strategies for Local Artists",
        0,
    ),
]

# Prep data
df = pd.DataFrame(data, columns=["url", "anchor_text", "label"])

if __name__ == "__main__":
    print("Starting Model Training for URL Ranking!")

    ranker = UrlRanker()
    ranker.train_model(df, save_path=MODEL_PATH)

    print("Model training complete!")
    print("Model has been saved successfully: model.pkl")
