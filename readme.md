Introduction:
    A REST API designed to generate PDF reports based on the recruitment assessment scores and the candidate's profile. Designed to be deployed on AWS. The PDF report will be saved in the results folder. All static images used to design the PDF report will be deleted after the PDF is built.

Base URL:
    /_reporting/

Error Handling:
    Raises an error if the input is not a nested dictionaries with values of type float, int, or string. 
    Returns a 500 error along with the message "Input must be nested dictionaries with values as either string, int, or float"

Endpoint:
    /generate_interview_questions_pdf
Description:
    generates the pdf report that customizes the interview questions for a given candidate
URL: 
    /candidate_reporting/generate_interview_questions_pdf
HTTP Method: 
    POST
Request Parameters:
    None
Request Headers:
    Content-type: Application/JSON
Request Body:
    A json blob of this format:
```json
  {
      "Purpose-driven": 6.5, 
      "Self-directedness": 7.5, 
      "Big Picture Thinking": 7.25, 
      "Exploring perspectives and alternatives": 4.5, 
      "Empowering others": 6.0, 
      "Role Modeling": 8.25, 
      "Understanding one”s emotions": 4.0, 
      "Self-control and regulation": 6.5, 
      "Speaking with conviction": 7.5, 
      "Empathetic": 4.0, 
      "Motivating and inspiring others": 8.0, 
      "Coaching": 5.0, 
      "Resilience": 8.0, 
      "Energy, passion and optimism": 6.5, 
      "Courage and risk-taking": 7.0, 
      "Driving change and innovation": 4.0, 
      "Dealing with uncertainty": 7.0, 
      "Instilling Trust": 6.0, 
      "Openness to feedback": 7.5, 
      "Collaboration Skills": 4.0, 
      "Fostering inclusiveness": 5.5, 
      "Organizational awareness": 6.0, 
      "Vision Alignment": 4.5, 
      "Time management and prioritization": 6.0, 
      "Promoting a culture of respect": 7.0, 
      "Unconventional approach": 5.0, 
      "Adaptability": 4.0, 
      "Attention to detail": 7.0, 
      "Planning": 6.5, 
      "Project management": 7.0, 
      "Critical Thinking": 8.0, 
      "Strategic Thinking": 7.5, 
      "Ownership and accountability": 5.5, 
      "Developing others": 7.0, 
      "Contextualization of knowledge": 6.0, 
      "candidate_profile": 
      {
          "name": "employee name", 
          "company_name": "company name"
      }
  }
```
The script will utilize both the assessment scores, candidate profile information, and the dynamic content from the two json files in order to populate the leadership report
