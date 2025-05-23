## Airflow User Exercise: Managing Users via the Web UI

In this hands-on exercise, you'll interact directly with Airflow's web UI to manage users and roles. You'll learn how to inspect users, understand what each role does, and create new users with different levels of access. The CLI is included after each step for reference, but you'll complete every task through the UI.

---

### Step 1: Access the Web UI

**In this step we will log in to the Airflow web interface** because it's a clear and reliable way to view and manage users, and that is useful for avoiding common mistakes or inconsistencies.

**Step 1a >** Open your browser and go to `http://localhost:8080`

**Step 1b >** Log in as the `admin` user (username and password were set up earlier).

**Step 1c >** From the top menu, click **Security** → **List Users**

**Reflection Questions:**
- Which users are listed?
- What roles do they have?
- 💡 CLI equivalent: `airflow users list`

---

### Step 2: Explore Roles and Permissions

**In this step we will examine built-in roles** because these determine what each user is allowed to do, and that is useful for controlling access at scale.

**Step 2a >** Go to **Security** → **List Roles**

**Step 2b >** Click on any role name (e.g., `Admin`, `User`, `Viewer`) to inspect what permissions it includes.

| Role     | Permissions                                                           |
|----------|------------------------------------------------------------------------|
| Admin    | Do everything — including user management and editing all DAGs.        |
| User     | View DAGs, trigger runs, check logs — but can’t edit or configure.     |
| Op       | Run and monitor DAGs, but not modify them.                             |
| Viewer   | Pure read-only access. Can browse, not touch.                          |
| Public   | Special role, no login needed — usually disabled.                      |

**Reflection Questions:**
- Which role would you give a new developer?
- Which one for a stakeholder?
- 💡 CLI equivalent: roles are not listed directly via CLI, but used in `airflow users create`

---

### Step 3: Add a New User (User Role)

**In this step we will create a new user with the `User` role** because this role lets someone test DAGs without making changes, and that is useful for safe development workflows.

**Step 3a >** Go to **Security** → **List Users** → click **+** (top right)

**Step 3b >** Fill out the form:
- Username: `newuser`
- First Name: `New`
- Last Name: `User`
- Email: `newuser@example.com`
- Password: `newpassword`
- Role: `User`

**Step 3c >** Click **Save**

**Reflection Questions:**
- What can this new user do?
- How would you give them more access later?
- 💡 CLI equivalent: `airflow users create --username newuser ...`

---

### Step 4: Add a Viewer User (Optional)

**In this step we will create a user with read-only access** because this is ideal for stakeholders or auditors, and that is useful when you want someone to observe but not interfere.

**Step 4a >** Repeat Step 3 with:
- Username: `alice`
- Role: `Viewer`

**Reflection Questions:**
- What does this user see in the UI?
- Can they run or edit DAGs?
- 💡 CLI equivalent: `airflow users create --username alice --role Viewer ...`

---

### Step 5: Create and Use a Custom Role

**In this step we will define a new role and assign it** because not all access needs are covered by the defaults, and that is useful for enforcing principle of least privilege.

**Step 5a >** Go to **Security** → **List Roles** → click **+**
- Role Name: `limited_trigger`

**Step 5b >** Assign these permissions:
- `can_dag_read` on all DAGs
- `can_dag_edit` on all DAGs
- (Optional: `can_log_read`, `can_taskinstance_read`)

**Step 5c >** Go to **Security** → **List Users** → click **+** and create:
- Username: `triggeruser`
- Role: `limited_trigger`

📝 Only Admins can create roles and assign permissions.

**Reflection Questions:**
- What permissions did you give this new role?
- When would you use it in a real team?
- 💡 CLI equivalent: Airflow does not support custom role creation via CLI, but roles can be assigned using `--role`

---

### Wrap-Up

✅ You now:
- Can navigate the Airflow web interface
- Know how to list and describe existing users
- Understand what each role can and can’t do
- Can safely create and manage users
- Can define and assign custom roles

🧠 These are real admin skills. You’ll need them as soon as you work with a team or move to production.

We’ll revisit this when setting up DAG ownership and permissions later in the week.
