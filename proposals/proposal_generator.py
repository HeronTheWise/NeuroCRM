def generate_proposal_from_template(project_name, project_type, client_brief):
    return f"""Dear Client,

Thank you for considering my services for your {project_type.lower()} project: *{project_name}*.

Based on your requirements, here's a customized proposal:

---

**Project Summary:**
{client_brief}

---

**Deliverables:**
- Strategy and planning
- Design & development
- Testing and delivery
- Support (as needed)

**Estimated Timeline:** 3–5 weeks  
**Estimated Budget:** Based on discussion

Let’s discuss further and finalize details.

Sincerely,  
[Your Name]
"""
