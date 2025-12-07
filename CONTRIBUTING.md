# **Contributing to OS-AMS**

First off, thank you for considering contributing to OS-AMS\! It's people like you that make the open-source community such an amazing place to learn, inspire, and create.

## **🤝 Getting Started**

### **1\. Fork the Repository**

If you are a new contributor, the standard workflow is to **Fork** the repository.

1. Click the "Fork" button at the top right of the GitHub page.  
2. This creates a copy of osams in your own GitHub account.

### **2\. Clone your Fork**

Clone *your* fork to your local machine:

git clone \[https://github.com/YOUR-USERNAME/osams.git\](https://github.com/YOUR-USERNAME/osams.git)  
cd osams

### **3\. Set Up the Development Environment**

Please refer to the [**Operations Guide**](https://www.google.com/search?q=OPS_GUIDE.md) for detailed setup instructions using Docker and TimescaleDB.

\# Quick setup  
cp .env.example .env  
docker-compose up \-d timescaledb  
./build\_manually.sh  
docker-compose up \-d

## **💻 Development Workflow**

### **1\. Create a Branch**

Always work on a new branch for each feature or bugfix. Do not work directly on main.

git checkout \-b feature/my-new-feature  
\# or  
git checkout \-b fix/login-issue

### **2\. Make Your Changes**

Write clean, maintainable code.

* **Python:** Follow PEP 8\. We use black for formatting.  
* **Frontend:** Use Bootstrap 5 utility classes where possible. Avoid inline CSS.

### **3\. Run Tests**

Before committing, ensure you haven't broken anything.

python manage.py test

### **4\. Commit Changes**

We encourage **Conventional Commits** to keep history readable:

* feat: add new gate allocation algorithm  
* fix: resolve sidebar rendering on mobile  
* docs: update installation steps

git commit \-m "feat: add new gate allocation algorithm"

### **5\. Push to Your Fork**

git push origin feature/my-new-feature

## **🔀 Submitting a Pull Request (PR)**

1. Go to the original Iotonix/osams repository on GitHub.  
2. You should see a prompt to **Compare & pull request**.  
3. **Title:** Describe the change clearly.  
4. **Description:** Reference any related Issue IDs (e.g., Closes \#123). Explain *what* you changed and *why*.  
5. Submit the PR.

**Code Review Process:**

* Maintainers will review your code.  
* They might request changes.  
* Once approved, your code will be merged into the main branch.

## **🐛 Reporting Bugs**

If you find a bug, please create a GitHub Issue including:

1. **Steps to Reproduce**: How can we make the bug happen?  
2. **Expected Behavior**: What should have happened?  
3. **Actual Behavior**: What actually happened?  
4. **Screenshots**: If applicable.

Thank you for helping make OS-AMS better\! ✈️