There are two python files used to generate the leadership assessment report:

The first file is called parser.py, which receieves a path to a csv file, which contains all of the textual data associated with generating the assessment report. It parses the data into two json files that that are used during the report generation process

The second file is called generate_pdf_report.py, which receieves a json payload contianing data tied to the user who has taken the report and their assessment scores. This is the format of the json payload:

'''json
{'Purpose-driven': 6.5, 'Self-directedness': 7.5, 'Big Picture Thinking': 7.25, 'Exploring perspectives and alternatives': 4.5, 'Empowering others': 6.0, 'Role Modeling': 8.25, "Understanding one's emotions": 4.0, 'Self-control and regulation': 6.5, 'Speaking with conviction': 7.5, 'Empathetic': 4.0, 'Motivating and inspiring others': 8.0, 'Coaching': 5.0, 'Resilience': 8.0, 'Energy, passion and optimism': 6.5, 'Courage and risk-taking': 7.0, 'Driving change and innovation': 4.0, 'Dealing with uncertainty': 7.0, 'Instilling Trust': 6.0, 'Openness to feedback': 7.5, 'Collaboration Skills': 4.0, 'Fostering inclusiveness': 5.5, 'Organizational awareness': 6.0, 'Vision Alignment': 4.5, 'Time management and prioritization': 6.0, 'Promoting a culture of respect': 7.0, 'Unconventional approach': 5.0, 'Adaptability': 4.0, 'Attention to detail': 7.0, 'Planning': 6.5, 'Project management': 7.0, 'Critical Thinking': 8.0, 'Strategic Thinking': 7.5, 'Ownership and accountability': 5.5, 'Developing others': 7.0, 'Contextualization of knowledge': 6.0, 'candidate_profile': {'name': 'employee name', 'company_name': 'company name'}}

The script will utilize both the assessment scores, candidate profile information, and the dynamic content from the two json files in order to populate the assessment report