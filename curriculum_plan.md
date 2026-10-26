# LET Review App — Curriculum Plan

## 1. Project Goal

Build a comprehensive, personalized review system for the Philippine Licensure Examination for Professional Teachers (LEPT).

The app must help users:
- Study all applicable examination subjects.
- Read lessons, notes, definitions, and examples.
- Learn formulas and follow step-by-step solutions.
- Practice questions and understand explanations.
- Identify weak topics and recurring mistakes.
- Review difficult topics repeatedly without neglecting other subjects.
- Track progress over time.
- Follow a personalized study schedule.

## 2. Official Sources

Use official PRC documents as the primary reference.

1. PRC Board Resolution No. 11, Series of 2025:
   Amending the Enhanced Table of Specifications for the LEPT.
      https://www.prc.gov.ph/sites/default/files/2025-11%20published%20PROFESSIONAL%20TEACHERS.pdf

      2. PRC guidelines on aligning the LEPT with the teacher education curriculum:
         https://prc.gov.ph/article/guidelines-implementation-prc-ched-jmc-alignment-lept-teacher-education-curriculum

         3. PRC Professional Regulatory Board for Professional Teachers:
            https://www.prc.gov.ph/Pages/PRBv4/ProfessionalTeachersv9.htm

            4. PRC examination programs:
               Check the latest applicable program before finalizing exam coverage and weights.

               IMPORTANT:
               Do not assume older examination requirements remain unchanged.
               Verify the applicable TOS, curriculum alignment rules, and examinee classification before finalizing the curriculum.

               ## 3. Examination Subjects

               The app must support the applicable combination of:

               - General Education
               - Professional Education
               - Specialization or major, when required

               The exact subjects and their weights must follow the applicable official PRC requirements.

               Do not assume that every examinee takes the same examination combination.

               ## 4. Examinee Classification

               Before creating the final personalized curriculum, determine:

               - Whether the examinee is applying for elementary or secondary level.
               - The examinee's degree and completed academic requirements.
               - The specialization or examination category accepted by PRC.
               - The applicable TOS and examination weights.

               The user's degree is BTVTED major in Food and Service Management.

               Do not automatically assume that this degree determines the exact examination category. Verify the applicable PRC eligibility and specialization requirements first.

               ## 5. Curriculum Mapping

               For every official subject and topic, record:

               - Subject
               - Main topic
               - Subtopic
               - Expected competency or learning outcome
               - Official source
               - Applicable examination weight, if specified
               - Verification status
               - Lesson status
               - Question bank status

               Verification status:
               - Verified from an official source
               - Needs further verification
               - Not yet mapped

               Never invent official examination weights or claim that an unverified topic is part of the official TOS.

               ## 6. Learning Materials

               Every topic should eventually contain:

               - Simple explanations
               - Important definitions
               - Detailed notes or handouts
               - Key concepts and facts
               - Examples
               - Formulas, when applicable
               - Step-by-step worked solutions
               - Common mistakes
               - Memory aids, when useful
               - Practice questions
               - Answer explanations
               - References or sources

               Use beginner-friendly language without removing important examination concepts.

               ## 7. Question Bank

               Each question should contain:

               - Unique question ID
               - Subject
               - Topic and subtopic
               - Question
               - Answer choices, when applicable
               - Correct answer
               - Explanation of the correct answer
               - Explanations of incorrect choices, when useful
               - Difficulty level
               - Learning competency
               - Source or verification status

               Questions should test different levels of learning, including remembering, understanding, applying, analyzing, and evaluating, where appropriate to the applicable TOS.

               Do not copy copyrighted review books or question banks without permission.

               ## 8. Mistake Tracking

               Record every attempt instead of keeping only the most recent answer.

               Track:
               - Question ID
               - Date and time
               - Selected answer
               - Correct or incorrect result
               - Confidence level
               - Whether the answer was guessed
               - Number of previous attempts
               - Previous mistakes
               - Topic mastery status

               A correct answer marked as a guess must not automatically count as mastery.

               Repeated mistakes should receive higher review priority.

               ## 9. Adaptive Review

               The system should:

               - Identify weak topics.
               - Detect repeated errors.
               - Prioritize topics with low accuracy.
               - Revisit guessed answers, even when correct.
               - Schedule topics for later review.
               - Increase review difficulty as mastery improves.
               - Continue covering the entire applicable curriculum.
               - Avoid repeatedly showing only the same few topics.

               The system must balance weak-topic practice with complete examination coverage.

               ## 10. Study Planner

               The study planner should support:

               - A flexible 24-week study program.
               - Daily and weekly study goals.
               - Work and commute schedules.
               - Meals and personal responsibilities.
               - Breaks and rest.
               - A target of 7–9 hours of sleep, when feasible.
               - Missed-study recovery plans.
               - Automatic adjustment based on progress and available time.

               Do not hardcode an examination date. Allow the user to enter or update it.

               ## 11. Dashboard

               Show:
               - Overall progress
               - Progress by examination subject
               - Topics completed
               - Topics not yet studied
               - Accuracy rate
               - Weakest topics
               - Repeated mistakes
               - Guessed answers requiring review
               - Upcoming review tasks
               - Study streak and study time, when available

               ## 12. Data Storage

               The app must eventually preserve progress after the browser closes or the app restarts.

               Store:
               - User settings
               - Study schedule
               - Quiz attempts
               - Mistake history
               - Topic mastery
               - Review schedules
               - Completed lessons

               Use a suitable persistent database or storage solution before treating progress tracking as complete.

               ## 13. Development Stages

               Stage 1: Verify official requirements and map the curriculum.

               Stage 2: Build the curriculum structure and lesson format.

               Stage 3: Create reliable learning materials.

               Stage 4: Develop the question bank and explanations.

               Stage 5: Implement full attempt history and mistake tracking.

               Stage 6: Build adaptive review and spaced repetition.

               Stage 7: Implement persistent storage.

               Stage 8: Improve the study planner and dashboard.

               Stage 9: Test accuracy, usability, and mobile compatibility.

               Stage 10: Prepare the app for secure deployment.

               ## 14. Current Status

               The app is an early Streamlit prototype.

               Completed:
               - Initial app structure
               - Basic navigation
               - Sample lessons and questions
               - Basic answer checking
               - Basic confidence selection
               - Initial project folders

               Not yet completed:
               - Verified complete curriculum
               - Comprehensive lesson library
               - Comprehensive question bank
               - Full quiz attempt history
               - Reliable adaptive review
               - Persistent progress storage
               - Complete personalized study planner
               - Production deployment

               Do not describe the app as a complete or officially validated LET reviewer until the relevant work has been completed and tested.
               ## 15. User's Examination Preparation Status

               - Degree: Bachelor of Technical-Vocational Teacher Education (BTVTEd)
               - Major: Food and Service Management
               - LET application status: Not yet applied
               - Eligibility status: Not yet confirmed by PRC

               ## 16. Curriculum Development Decision

               Use the applicable PRC requirements for BTVTEd as the starting point.

               The planned examination areas are:
               - General Education
               - Professional Education
               - Technical-Vocational Teacher Education (TVTEd) specialization focused on introductory courses and common competencies, subject to verification against the applicable official documents.

               Do not automatically substitute Home Economics or another specialization for TVTEd.

               Before finalizing the user's examination path, confirm the applicable requirements with PRC.

               Do not invent examination weights, topics, or eligibility rules.

               ## 17. Mandatory Original AI-Assisted Content Policy

               All lessons, handouts, explanations, examples, formulas and worked solutions, practice questions, answer keys, and mock examinations must be developed as original learning materials with AI assistance.

               Do not plagiarize, reproduce, or improperly adapt copyrighted review materials from other review centers, textbooks, websites, or content creators.

               Use official examination requirements to map the curriculum. Use appropriate educational references to verify facts. Write original explanations and examples, and create original practice questions.

               Record sources and applicable licenses or permissions.

               Review factual accuracy, answer correctness, curriculum alignment, and originality before approving content for learners.

               AI-generated content must not automatically be considered accurate, original, or legally cleared.

               Clearly distinguish verified examination requirements from supplementary content and requirements that still need confirmation.
        
               ## 18. Complete TLE Learning Library

               The application must provide a broad learning library covering all four
               Technology and Livelihood Education (TLE) branches.

               ### Branch 1: Agriculture and Fishery Arts (AFA)
               Develop learning materials for applicable agricultural and fishery topics.

               ### Branch 2: Home Economics (HE)
               Develop learning materials for applicable home economics topics, including
               food preparation, hospitality, and related competencies.

               ### Branch 3: Information and Communications Technology (ICT)
               Develop learning materials for applicable computer, networking, programming,
               and digital technology topics.

               ### Branch 4: Industrial Arts (IA)
               Develop learning materials for applicable construction, electrical,
               automotive, metalwork, electronics, and related competencies.

               ### Curriculum Verification Rules

               The four branches form the broad TLE learning library.

               Do not automatically assume that all four branches are required examination
               subjects for every examinee.

               Separate the complete learning library from the verified examination
               requirements for each degree pathway and examinee category.

               Use the applicable official PRC Table of Specifications and curriculum
               alignment requirements to determine which content belongs in the core
               examination reviewer.

               Mark additional content as supplementary when its examination relevance
               has not been verified.

               ### Original AI-Assisted Content

               Create original lessons, handouts, explanations, examples, practice questions,
               answer keys, and mock examinations for the learning library.

               Do not plagiarize or reproduce unauthorized materials from other review
               centers, textbooks, websites, or content creators.

               Verify factual accuracy, record sources, and review originality before
               approving materials for learners.
               