
import csv
import os
import random
from datetime import datetime, timedelta, time

# ============================================================
# Reference / lookup data
# ============================================================

FIRST_NAMES_M = [
    "Ahmed", "Mohamed", "Mahmoud", "Youssef", "Omar", "Ali", "Khaled",
    "Karim", "Amr", "Hassan", "Mostafa", "Tarek", "Sherif", "Ibrahim",
    "Hossam", "Ayman", "Waleed", "Adham", "Fady", "Ziad", "Marwan",
    "Hazem", "Sameh", "Nabil", "Ashraf",
]
FIRST_NAMES_F = [
    "Fatma", "Mariam", "Nour", "Sara", "Yasmin", "Aya", "Salma", "Heba",
    "Rania", "Dina", "Mona", "Nada", "Rana", "Hana", "Doaa", "Reem",
    "Shorouk", "Menna", "Farida", "Aliaa", "Basma", "Eman", "Ghada",
    "Laila", "Wafaa",
]
LAST_NAMES = [
    "Hassan", "Mohamed", "Ibrahim", "Ali", "Youssef", "Mahmoud", "Farouk",
    "El-Sayed", "Abdelrahman", "Kamel", "Adel", "Fathy", "Nasser", "Aziz",
    "Saeed", "Gaber", "Shaker", "Rashad", "Naguib", "Fahmy", "Ezzat",
    "Salem", "Zaki", "Hamdy", "Soliman",
]

DEPARTMENTS = ["IT", "Operations", "Sales", "Marketing", "Finance", "HR"]

JOB_TITLES_BY_DEPT = {
    "IT": ["Software Engineer", "Data Engineer", "Data Scientist",
           "DevOps Engineer", "QA Engineer", "IT Support",
           "System Administrator", "Data Analyst"],
    "Operations": ["Operations Analyst", "Operations Manager",
                   "Logistics Coordinator", "Supply Chain Analyst",
                   "Warehouse Supervisor"],
    "Sales": ["Sales Representative", "Account Executive",
              "Sales Manager", "Business Development", "Key Account Manager"],
    "Marketing": ["Marketing Specialist", "Content Creator",
                  "SEO Specialist", "Marketing Manager", "Brand Manager"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager",
                "Auditor", "Payroll Specialist"],
    "HR": ["HR Specialist", "Recruiter", "Hiring Manager", "HR Manager",
           "Talent Acquisition"],
}

# job titles that are allowed to run interviews / post jobs
RECRUITING_TITLES = {"HR Specialist", "Recruiter", "Hiring Manager",
                      "HR Manager", "Talent Acquisition"}

JOB_LEVELS = ["Junior", "Mid", "Senior", "Manager"]
SALARY_RANGES = {
    "Junior": (8000, 15000),
    "Mid": (15000, 28000),
    "Senior": (28000, 45000),
    "Manager": (45000, 80000),
}

PLATFORMS = ["LinkedIn", "Website", "Wuzzuf", "Indeed"]
EDUCATION_LEVELS = ["High School", "Bachelor", "Master", "PhD"]
GENDERS = ["Male", "Female"]
INTERVIEW_STAGES = ["HR", "Technical", "Hiring Manager"]
INTERVIEW_RESULTS = ["Pass", "Fail", "Pending"]
SEPARATION_TYPES = ["Resignation", "Termination", "Fired"]
SEPARATION_REASONS = {
    "Resignation": ["Better opportunity", "Relocation", "Career change",
                    "Higher education", "Personal reasons"],
    "Termination": ["Performance issues", "Restructuring",
                     "Redundancy", "Policy violation"],
    "Fired": ["Gross misconduct", "Policy violation", "Attendance issues",
              "Performance issues"],
}

random.seed(42)

# ============================================================
# Helpers
# ============================================================

def random_person_name():
    gender = random.choice(GENDERS)
    first = random.choice(FIRST_NAMES_M if gender == "Male" else FIRST_NAMES_F)
    last = random.choice(LAST_NAMES)
    return first, last, gender


def random_date(start: datetime, end: datetime) -> datetime:
    """Random date (no time component) between start and end inclusive."""
    if start >= end:
        return min(start, end)
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def random_datetime(start: datetime, end: datetime) -> datetime:
    """Random datetime (with time + microseconds) between start and end."""
    if start >= end:
        # degenerate/inverted window: clamp hard, no jitter (jitter could
        # push the result past `end`, which downstream code relies on
        # never happening)
        return min(start, end)
    delta_seconds = int((end - start).total_seconds())
    offset = random.randint(0, delta_seconds)
    dt = start + timedelta(seconds=offset)
    dt = dt.replace(microsecond=random.randint(0, 999) * 1000)
    return dt


def fmt_date(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def fmt_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S.") + f"{dt.microsecond // 1000:03d}"


def fmt_time(t: time) -> str:
    return t.strftime("%H:%M:%S")


def random_scheduled_time() -> time:
    hour = random.choice([8, 9, 10])
    minute = random.choice([0, 15, 30, 45])
    return time(hour=hour, minute=minute, second=0)


def make_email(first, last, uniq_id):
    domain = random.choice(["gmail.com", "outlook.com", "yahoo.com", "company-mail.com"])
    return f"{first.lower()}.{last.lower()}{uniq_id}@{domain}"


def make_phone():
    return "01" + str(random.choice([0, 1, 2, 5])) + "".join(str(random.randint(0, 9)) for _ in range(8))


def created_updated(base_dt: datetime, end_of_range: datetime):
    """created_at then a later (or equal) updated_at, both within range."""
    created = random_datetime(base_dt, end_of_range)
    updated = random_datetime(created, end_of_range)
    return created, updated


def gen_offered_salary(min_s, max_s):
    return round(random.uniform(min_s, max_s), 2)


# ============================================================
# Core dataset generator
# ============================================================

def generate_dataset(start_date, end_date, counts, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    n_employees = counts["employees"]
    n_departments = counts["departments"]
    n_jobs = counts["jobs"]
    n_postings = counts["postings"]
    n_candidates = counts["candidates"]
    n_applications = counts["applications"]
    n_interviews = counts["interviews"]
    n_offers = counts["offers"]
    n_terminated = counts["terminated"]
    n_accepted_offers = counts["accepted_offers"]
    bonus_prob = counts.get("bonus_prob", 0.35)

    # ------------------------------------------------------------------
    # 1. Departments (skeleton first, manager assigned after employees)
    # ------------------------------------------------------------------
    dept_names = DEPARTMENTS[:n_departments] if n_departments <= len(DEPARTMENTS) else \
        DEPARTMENTS + [f"Dept{i}" for i in range(len(DEPARTMENTS), n_departments)]

    departments = []
    for i, name in enumerate(dept_names, start=1):
        created, updated = created_updated(start_date, end_date)
        departments.append({
            "department_id": f"dept_{i}",
            "department_name": name,
            "manager_id": None,  # filled later
            "created_at": created,
            "updated_at": updated,
        })
    dept_by_name = {d["department_name"]: d for d in departments}

    # ------------------------------------------------------------------
    # 2. Jobs
    # ------------------------------------------------------------------
    jobs = []
    jobs_by_dept = {name: [] for name in dept_names}
    for i in range(1, n_jobs + 1):
        dept_name = random.choice(dept_names)
        title = random.choice(JOB_TITLES_BY_DEPT.get(dept_name, ["General Staff"]))
        level = random.choice(JOB_LEVELS)
        lo, hi = SALARY_RANGES[level]
        min_salary = round(random.uniform(lo, lo * 1.15), 2)
        max_salary = round(random.uniform(hi * 0.9, hi), 2)
        if max_salary < min_salary:
            min_salary, max_salary = max_salary, min_salary
        created, updated = created_updated(start_date, end_date)
        job = {
            "job_id": f"job_{i}",
            "job_department": dept_name,
            "job_title": title,
            "job_level": level,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "created_at": created,
            "updated_at": updated,
        }
        jobs.append(job)
        jobs_by_dept[dept_name].append(job)

    # make sure every department has at least one job
    for name in dept_names:
        if not jobs_by_dept[name]:
            title = random.choice(JOB_TITLES_BY_DEPT.get(name, ["General Staff"]))
            level = random.choice(JOB_LEVELS)
            lo, hi = SALARY_RANGES[level]
            created, updated = created_updated(start_date, end_date)
            job = {
                "job_id": f"job_{len(jobs) + 1}",
                "job_department": name,
                "job_title": title,
                "job_level": level,
                "min_salary": round(lo, 2),
                "max_salary": round(hi, 2),
                "created_at": created,
                "updated_at": updated,
            }
            jobs.append(job)
            jobs_by_dept[name].append(job)

    # recruiting-eligible jobs (HR side) used for interviewer / poster pool
    recruiting_jobs = [j for j in jobs if j["job_title"] in RECRUITING_TITLES]
    if not recruiting_jobs:
        # guarantee at least a couple of HR jobs exist
        for title in ["HR Specialist", "Recruiter"]:
            created, updated = created_updated(start_date, end_date)
            job = {
                "job_id": f"job_{len(jobs) + 1}",
                "job_department": "HR",
                "job_title": title,
                "job_level": "Mid",
                "min_salary": SALARY_RANGES["Mid"][0],
                "max_salary": SALARY_RANGES["Mid"][1],
                "created_at": created,
                "updated_at": updated,
            }
            jobs.append(job)
            jobs_by_dept.setdefault("HR", []).append(job)
            recruiting_jobs.append(job)

    # ------------------------------------------------------------------
    # 3. Employees
    # ------------------------------------------------------------------
    terminated_idx = set(random.sample(range(1, n_employees + 1),
                                        min(n_terminated, n_employees)))

    employees = []
    employees_by_dept = {name: [] for name in dept_names}
    recruiting_employees = []

    for i in range(1, n_employees + 1):
        dept_name = random.choice(dept_names)
        dept_jobs = jobs_by_dept[dept_name]
        job = random.choice(dept_jobs)
        first, last, gender = random_person_name()
        email = make_email(first, last, i)
        phone = make_phone()
        dob = random_date(datetime(1970, 1, 1), datetime(2003, 12, 31))

        # hire date somewhere in [start_date, end_date]
        hire_date = random_date(start_date, end_date)

        is_terminated = i in terminated_idx
        termination_date = None
        status = "Active"
        if is_terminated:
            # termination after hire, within range
            if hire_date < end_date:
                termination_date = random_date(hire_date + timedelta(days=1), end_date)
            else:
                termination_date = hire_date
            status = "Terminated"

        education = random.choice(EDUCATION_LEVELS)
        created, updated = created_updated(
            datetime.combine(hire_date.date(), time(0, 0)), end_date
        )

        emp = {
            "employee_id": f"emp_{i}",
            "first_name": first,
            "last_name": last,
            "email": email,
            "phone": phone,
            "gender": gender,
            "date_of_birth": dob,
            "hire_date": hire_date,
            "termination_date": termination_date,
            "department_id": dept_by_name[dept_name]["department_id"],
            "job_id": job["job_id"],
            "manager_id": None,  # filled below
            "status": status,
            "education_level": education,
            "created_at": created,
            "updated_at": updated,
            "_dept_name": dept_name,
            "_job_title": job["job_title"],
            "_job_level": job["job_level"],
            "_job": job,
        }
        employees.append(emp)
        employees_by_dept[dept_name].append(emp)
        if job["job_title"] in RECRUITING_TITLES:
            recruiting_employees.append(emp)

    # guarantee at least some recruiting employees exist
    if not recruiting_employees:
        for e in random.sample(employees, min(5, len(employees))):
            e["_job_title"] = "HR Specialist"
            recruiting_employees.append(e)

    # assign department managers + employee manager_id (single-level hierarchy)
    for dept_name in dept_names:
        dept_employees = employees_by_dept[dept_name]
        if not dept_employees:
            continue
        managers = [e for e in dept_employees if e["_job_level"] == "Manager"]
        head = random.choice(managers) if managers else random.choice(dept_employees)
        head["manager_id"] = None
        dept_by_name[dept_name]["manager_id"] = head["employee_id"]
        for e in dept_employees:
            if e is not head:
                e["manager_id"] = head["employee_id"]

    # ------------------------------------------------------------------
    # 4. Postings
    # ------------------------------------------------------------------
    postings = []
    for i in range(1, n_postings + 1):
        job = random.choice(jobs)
        poster = random.choice(recruiting_employees)
        posted_at = random_datetime(start_date, end_date - timedelta(days=1)
                                     if end_date > start_date else end_date)
        max_expiry = min(posted_at + timedelta(days=60), end_date)
        expires_at = random_datetime(posted_at, max_expiry) if max_expiry > posted_at else posted_at
        created, updated = created_updated(posted_at, end_date)
        postings.append({
            "posting_id": f"post_{i}",
            "job_id": job["job_id"],
            "posted_by": poster["employee_id"],
            "platform": random.choice(PLATFORMS),
            "posted_at": posted_at,
            "expires_at": expires_at,
            "created_at": created,
            "updated_at": updated,
            "_job": job,
        })

    postings_by_job = {}
    for p in postings:
        postings_by_job.setdefault(p["_job"]["job_id"], []).append(p)

    # ------------------------------------------------------------------
    # 5. Candidates
    # ------------------------------------------------------------------
    candidates = []
    for i in range(1, n_candidates + 1):
        first, last, _ = random_person_name()
        email = make_email(first, last, f"c{i}")
        phone = make_phone()
        created, updated = created_updated(start_date, end_date)
        candidates.append({
            "candidate_id": f"cand_{i}",
            "first_name": first,
            "last_name": last,
            "email": email,
            "phone": phone,
            "created_at": created,
            "updated_at": updated,
        })

    # ------------------------------------------------------------------
    # 6. Applications
    # ------------------------------------------------------------------
    applications = []
    for i in range(1, n_applications + 1):
        posting = random.choice(postings)
        job = posting["_job"]
        candidate = random.choice(candidates)
        lo = posting["posted_at"]
        hi = max(posting["expires_at"], lo)
        application_date = random_datetime(lo, hi)
        created, updated = created_updated(application_date, end_date)
        applications.append({
            "application_id": f"app_{i}",
            "candidate_id": candidate["candidate_id"],
            "job_id": job["job_id"],
            "post_id": posting["posting_id"],
            "application_date": application_date,
            "source": posting["platform"],
            "created_at": created,
            "updated_at": updated,
            "_job": job,
            "_posting": posting,
        })

    # ------------------------------------------------------------------
    # 7 & 8. Interviews + Offers (interlinked)
    # ------------------------------------------------------------------
    offer_apps = random.sample(applications, min(n_offers, len(applications)))
    n_hired = min(n_accepted_offers, len(offer_apps))
    hired_apps = offer_apps[:n_hired]
    hired_app_ids = {a["application_id"] for a in hired_apps}

    interviews = []
    interview_seq = 0

    HIRE_STAGES = ["HR", "Technical", "Hiring Manager"]  # exactly one pass per stage

    # 7a. Guaranteed 3 passed interviews for every application that will be hired
    for application in hired_apps:
        cursor = application["application_date"]
        for stage in HIRE_STAGES:
            interview_seq += 1
            cursor = random_datetime(
                cursor + timedelta(days=1),
                min(cursor + timedelta(days=10), end_date)
            )
            score = round(random.uniform(70.1, 100.0), 1)  # strictly > 70
            created, updated = created_updated(cursor, end_date)
            interviews.append({
                "interview_id": f"int_{interview_seq}",
                "application_id": application["application_id"],
                "interviewer_id": random.choice(recruiting_employees)["employee_id"],
                "interview_stage": stage,
                "interview_date": cursor,
                "score": score,
                "result": "Pass",
                "created_at": created,
                "updated_at": updated,
            })

    # 7b. Fill the remaining interview budget with random applications/results
    remaining = max(0, n_interviews - len(interviews))
    for _ in range(remaining):
        interview_seq += 1
        application = random.choice(applications)
        interview_date = random_datetime(
            application["application_date"],
            min(application["application_date"] + timedelta(days=30), end_date)
        )
        result = random.choice(INTERVIEW_RESULTS)
        if result == "Pass":
            score = round(random.uniform(70.1, 100.0), 1)   # Pass => score > 70
        elif result == "Pending":
            score = None
        else:  # Fail
            score = round(random.uniform(0, 70.0), 1)       # Fail => score <= 70
        created, updated = created_updated(interview_date, end_date)
        interviews.append({
            "interview_id": f"int_{interview_seq}",
            "application_id": application["application_id"],
            "interviewer_id": random.choice(recruiting_employees)["employee_id"],
            "interview_stage": random.choice(INTERVIEW_STAGES),
            "interview_date": interview_date,
            "score": score,
            "result": result,
            "created_at": created,
            "updated_at": updated,
        })

    # index the latest interview date per application, needed so an
    # offer for a hired application is always dated after its 3 passes
    last_interview_date_by_app = {}
    for iv in interviews:
        app_id = iv["application_id"]
        if app_id not in last_interview_date_by_app or iv["interview_date"] > last_interview_date_by_app[app_id]:
            last_interview_date_by_app[app_id] = iv["interview_date"]

    # ------------------------------------------------------------------
    # 8. Offers
    # ------------------------------------------------------------------
    offers = []
    for i, application in enumerate(offer_apps, start=1):
        accepted = application["application_id"] in hired_app_ids
        job = application["_job"]

        offer_date = random_datetime(
            application["application_date"] + timedelta(days=1),
            min(application["application_date"] + timedelta(days=45), end_date)
        )
        if accepted:
            # push the offer to after the 3 passed interviews finished
            last_iv = last_interview_date_by_app.get(application["application_id"])
            if last_iv is not None:
                earliest_possible = last_iv + timedelta(days=1)
                offer_date = max(offer_date, earliest_possible)
                offer_date = min(offer_date, end_date)

        expiry_date = random_datetime(offer_date, min(offer_date + timedelta(days=21), end_date))
        acceptance_date = None
        if accepted and expiry_date >= offer_date:
            acceptance_date = random_datetime(offer_date, expiry_date)
        created, updated = created_updated(offer_date, end_date)
        offers.append({
            "offer_id": f"off_{i}",
            "application_id": application["application_id"],
            "job_id": job["job_id"],
            "candidate_id": application["candidate_id"],
            "offered_salary": gen_offered_salary(job["min_salary"], job["max_salary"]),
            "offer_date": offer_date,
            "expiry_date": expiry_date,
            "acceptance_date": acceptance_date,
            "created_at": created,
            "updated_at": updated,
        })

    # ------------------------------------------------------------------
    # 9. Separations (one per terminated employee)
    # ------------------------------------------------------------------
    separations = []
    terminated_employees = [e for e in employees if e["status"] == "Terminated"]
    for i, e in enumerate(terminated_employees, start=1):
        sep_type = random.choice(SEPARATION_TYPES)
        reason = random.choice(SEPARATION_REASONS[sep_type])
        last_working_day = e["termination_date"]
        created, updated = created_updated(
            datetime.combine(last_working_day.date(), time(0, 0)), end_date
        )
        separations.append({
            "employee_id": e["employee_id"],
            "type": sep_type,
            "reason": reason,
            "last_working_day": last_working_day,
            "created_at": created,
            "updated_at": updated,
        })

    # ------------------------------------------------------------------
    # 10. Payroll (grain: employee x month) -> stream to file
    # ------------------------------------------------------------------
    payroll_path = os.path.join(out_dir, "payroll_table.csv")
    payroll_id = 0
    with open(payroll_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["payroll_id", "employee_id", "salary", "bonus",
                          "deductions", "tax", "net_salary", "payment_date",
                          "created_at", "updated_at"])
        for e in employees:
            job = e["_job"]
            base_salary = round(random.uniform(job["min_salary"], job["max_salary"]), 2)
            period_end = e["termination_date"] if e["termination_date"] else end_date
            period_end = min(period_end, end_date)
            month_cursor = e["hire_date"].replace(day=1)
            while month_cursor <= period_end:
                payroll_id += 1
                bonus = round(random.uniform(500, 5000), 2) if random.random() < bonus_prob else 0.0
                deductions = round(random.uniform(0, 800), 2)
                gross = base_salary + bonus
                tax = round(gross * random.uniform(0.05, 0.15), 2)
                net_salary = round(gross - deductions - tax, 2)
                # payment on the last day of that month, capped at period_end
                if month_cursor.month == 12:
                    next_month = month_cursor.replace(year=month_cursor.year + 1, month=1)
                else:
                    next_month = month_cursor.replace(month=month_cursor.month + 1)
                last_day_of_month = next_month - timedelta(days=1)
                payment_date = min(last_day_of_month, period_end)
                created, updated = created_updated(
                    datetime.combine(payment_date.date(), time(0, 0)), end_date
                )
                writer.writerow([
                    f"pay_{payroll_id}", e["employee_id"], base_salary, bonus,
                    deductions, tax, net_salary, fmt_date(payment_date),
                    fmt_ts(created), fmt_ts(updated),
                ])
                month_cursor = next_month


    # ------------------------------------------------------------------
    # Write the remaining (smaller) tables
    # ------------------------------------------------------------------
    with open(os.path.join(out_dir, "department_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["department_id", "department_name", "manager_id", "created_at", "updated_at"])
        for d in departments:
            writer.writerow([d["department_id"], d["department_name"], d["manager_id"],
                              fmt_ts(d["created_at"]), fmt_ts(d["updated_at"])])

    with open(os.path.join(out_dir, "jobs_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["job_id", "job_department", "job_title", "job_level",
                          "min_salary", "max_salary", "created_at", "updated_at"])
        for j in jobs:
            writer.writerow([j["job_id"], j["job_department"], j["job_title"], j["job_level"],
                              j["min_salary"], j["max_salary"],
                              fmt_ts(j["created_at"]), fmt_ts(j["updated_at"])])

    with open(os.path.join(out_dir, "employee_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["employee_id", "first_name", "last_name", "email", "phone", "gender",
                          "date_of_birth", "hire_date", "termination_date", "department_id",
                          "job_id", "manager_id", "status", "education_level",
                          "created_at", "updated_at"])
        for e in employees:
            writer.writerow([
                e["employee_id"], e["first_name"], e["last_name"], e["email"], e["phone"],
                e["gender"], fmt_date(e["date_of_birth"]), fmt_date(e["hire_date"]),
                fmt_date(e["termination_date"]) if e["termination_date"] else "",
                e["department_id"], e["job_id"], e["manager_id"] if e["manager_id"] else "",
                e["status"], e["education_level"],
                fmt_ts(e["created_at"]), fmt_ts(e["updated_at"]),
            ])

    with open(os.path.join(out_dir, "posting_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["posting_id", "job_id", "posted_by", "platform", "posted_at",
                          "expires_at", "created_at", "updated_at"])
        for p in postings:
            writer.writerow([p["posting_id"], p["job_id"], p["posted_by"], p["platform"],
                              fmt_ts(p["posted_at"]), fmt_ts(p["expires_at"]),
                              fmt_ts(p["created_at"]), fmt_ts(p["updated_at"])])

    with open(os.path.join(out_dir, "candidate_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "first_name", "last_name", "email", "phone",
                          "created_at", "updated_at"])
        for c in candidates:
            writer.writerow([c["candidate_id"], c["first_name"], c["last_name"], c["email"],
                              c["phone"], fmt_ts(c["created_at"]), fmt_ts(c["updated_at"])])

    with open(os.path.join(out_dir, "application_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["application_id", "candidate_id", "job_id", "post_id",
                          "application_date", "source", "created_at", "updated_at"])
        for a in applications:
            writer.writerow([a["application_id"], a["candidate_id"], a["job_id"], a["post_id"],
                              fmt_ts(a["application_date"]), a["source"],
                              fmt_ts(a["created_at"]), fmt_ts(a["updated_at"])])

    with open(os.path.join(out_dir, "interview_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["interview_id", "application_id", "interviewer_id", "interview_stage",
                          "interview_date", "score", "result", "created_at", "updated_at"])
        for iv in interviews:
            writer.writerow([iv["interview_id"], iv["application_id"], iv["interviewer_id"],
                              iv["interview_stage"], fmt_ts(iv["interview_date"]),
                              iv["score"] if iv["score"] is not None else "", iv["result"],
                              fmt_ts(iv["created_at"]), fmt_ts(iv["updated_at"])])

    with open(os.path.join(out_dir, "offers_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["offer_id", "application_id", "job_id", "candidate_id",
                          "offered_salary", "offer_date", "expiry_date", "acceptance_date",
                          "created_at", "updated_at"])
        for o in offers:
            writer.writerow([o["offer_id"], o["application_id"], o["job_id"], o["candidate_id"],
                              o["offered_salary"], fmt_ts(o["offer_date"]),
                              fmt_ts(o["expiry_date"]),
                              fmt_ts(o["acceptance_date"]) if o["acceptance_date"] else "",
                              fmt_ts(o["created_at"]), fmt_ts(o["updated_at"])])

    with open(os.path.join(out_dir, "separations_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["employee_id", "type", "reason", "last_working_day",
                          "created_at", "updated_at"])
        for s in separations:
            writer.writerow([s["employee_id"], s["type"], s["reason"],
                              fmt_date(s["last_working_day"]),
                              fmt_ts(s["created_at"]), fmt_ts(s["updated_at"])])

    print(f"[{out_dir}] employees={len(employees)} departments={len(departments)} "
          f"jobs={len(jobs)} postings={len(postings)} candidates={len(candidates)} "
          f"applications={len(applications)} interviews={len(interviews)} "
          f"(forced pass-3-interview hires: {len(hired_apps) * 3}) "
          f"offers={len(offers)} (accepted={sum(1 for o in offers if o['acceptance_date'])}) "
          f"separations={len(separations)} terminated_target={n_terminated}")


# ============================================================
# Configs & entry point
# ============================================================

def main():
    base_dir = os.getcwd()

    prod_start = datetime(2025, 1, 1)
    prod_end = datetime(2026, 6, 30)
    prod_counts = {
        "employees": 700,
        "departments": 6,
        "jobs": 210,
        "postings": 150,
        "candidates": 2000,
        "applications": 2500,
        "interviews": 1000,
        "offers": 400,
        "terminated": 65,
        "accepted_offers": 90,
        "bonus_prob": 0.35,
    }

    dev_start = datetime(2026, 1, 1)
    dev_end = datetime(2026, 3, 31)
    scale = 0.20
    dev_counts = {
        "employees": max(1, round(prod_counts["employees"] * scale)),
        "departments": prod_counts["departments"],
        "jobs": max(1, round(prod_counts["jobs"] * scale)),
        "postings": max(1, round(prod_counts["postings"] * scale)),
        "candidates": max(1, round(prod_counts["candidates"] * scale)),
        "applications": max(1, round(prod_counts["applications"] * scale)),
        "interviews": max(1, round(prod_counts["interviews"] * scale)),
        "offers": max(1, round(prod_counts["offers"] * scale)),
        "terminated": max(1, round(prod_counts["terminated"] * scale)),
        "accepted_offers": max(1, round(prod_counts["accepted_offers"] * scale)),
        "bonus_prob": prod_counts["bonus_prob"],
    }

    print("Generating prod_folder ...")
    generate_dataset(prod_start, prod_end, prod_counts, os.path.join(base_dir, "prod_folder"))

    print("Generating dev_folder ...")
    generate_dataset(dev_start, dev_end, dev_counts, os.path.join(base_dir, "dev_folder"))

    print("Done.")


if __name__ == "__main__":
    main()