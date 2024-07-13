from flask import Flask, render_template, request, session, jsonify
import openai
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app.secret_key = os.getenv("SECRET_KEY")

# Initial questions
questions = [
    "To gain further understanding, can you please describe your educational experience?",
    "What are your aspirations and higher education goals (e.g., want to study abroad or at elite universities)?",
    "Please describe if there are any financial constraints?"
]

# Options to present after initial questions
final_options = [
    "Would you like a detailed roadmap to achieve your career goals considering your academics, financial status, and study locations?",
    "Do you want personalized career guidance based on your academic performance, financial status, and desired study locations?",
    "Do you need other specific guidance like scholarship opportunities, study programs, or financial planning?",
    "Other"
]

# Context variables
pathway_generated = False
intent = None
current_pathway_step = None

@app.route('/')
def home():
    session.clear()
    session['question_index'] = -1  # Start with the greeting
    session['user_responses'] = []
    global pathway_generated
    pathway_generated = False
    global intent
    intent = None
    global current_pathway_step
    current_pathway_step = None
    return render_template('chat.html')

@app.route('/process_chat', methods=['POST'])
def process_chat():
    user_input = request.form.get('user_input')
    
    if user_input:
        global pathway_generated
        global intent
        global current_pathway_step
        
        if pathway_generated:
            if current_pathway_step and "explain" in user_input.lower():
                # Handle request to explain a specific step in the pathway
                explanation = explain_pathway_step(current_pathway_step)
                return jsonify({'response': explanation})
            
            # Handle unrelated queries or fallback responses
            response = handle_unrelated_query(user_input)
            return jsonify({'response': response})

        question_index = session.get('question_index', -1)
        user_responses = session.get('user_responses', [])
        
        if question_index == -1:
            session['question_index'] = 0
            return jsonify({'question': questions[0]})
        
        user_responses.append(user_input)
        session['user_responses'] = user_responses
        
        if question_index < len(questions):
            question_index += 1
            session['question_index'] = question_index
            
            if question_index < len(questions):
                return jsonify({'question': questions[question_index]})
            else:
                return jsonify({'options': final_options})
        
        else:
            try:
                bot_response = get_ai_response(user_responses)
                return jsonify({'response': bot_response})
            except openai.error.RateLimitError:
                return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
            except openai.error.OpenAIError as e:
                app.logger.error(f"OpenAI API error: {str(e)}")
                return jsonify({'error': 'Sorry, something went wrong with the AI service. Please try again later.'}), 500
    
    return jsonify({'error': 'Invalid input'}), 400

def get_ai_response(user_responses):
    messages = [
        {"role": "system", "content": "You are a helpful assistant providing detailed and clear guidance to students."}
    ]
    
    for response in user_responses:
        messages.append({"role": "user", "content": response})
    
    final_prompt = (
        "Generate three distinct pathways to help the student achieve their goal and studying at their dreamed University. Each pathway should be detailed and clearly separated, covering academic preparation, standardized tests, application strategies, financial planning, and any additional tips with web links specific to each pathway."
        "Each pathway should be clearly separated and include step-by-step guidance on academic focus, extracurricular activities, standardized tests, undergraduate education, gaining relevant experience, financial planning, residency, licensing, and additional tips."
        "Each step should be detailed and easy to understand. Provide specific resources, examples, and tips to help the user along the way."
        "After that generating pathways if the student asks to explain any point or any step in detailed way . explain that step or point in detailed manner "
        "generate the correct answers for the question which the student asks"
    )
    
    messages.append({"role": "user", "content": final_prompt})
    
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=4096,
            temperature=0.7,
            top_p=1
        )
        return completion.choices[0].message['content']
    
    except openai.error.RateLimitError as e:
        raise
    except openai.error.OpenAIError as e:
        raise RuntimeError(f"Error from OpenAI API: {str(e)}")

def explain_pathway_step(step_number):
    global current_pathway_step
    
    if step_number == 1:
        explanation = "To excel in academic preparation for Princeton, focus on maintaining high grades in subjects like Math, Physics, and Chemistry. Consider taking advanced courses if available."
    elif step_number == 2:
        explanation = "Start preparing early for standardized tests like SAT/ACT. Use resources like Khan Academy for SAT preparation."
    elif step_number == 3:
        explanation = "Engage in extracurricular activities related to aeronautical engineering, such as science clubs or internships."
    elif step_number == 4:
        explanation = "Craft a strong application by focusing on your personal statement and obtaining strong letters of recommendation."
    elif step_number == 5:
        explanation = "Research and apply for scholarships and financial aid programs to fund your education."
    elif step_number == 6:
        explanation = "If possible, visit Princeton University to familiarize yourself with the campus and network with current students and faculty."
    else:
        explanation = "I'm sorry, I don't have details on that specific step. Please ask about another point in the pathway."
    
    current_pathway_step = None  # Reset current_pathway_step after explanation
    return explanation

def handle_unrelated_query(user_input):
    global intent
    
    # Implement intent recognition logic based on user_input
    # Example: intent recognition based on keywords or NLU libraries like spaCy
    
    if 'career' in user_input.lower():
        intent = 'career_advice'
        return provide_career_advice()
    elif 'test' in user_input.lower():
        intent = 'test_preparation'
        return provide_test_preparation_tips()
    elif 'explain' in user_input.lower():
        return "I can explain specific steps in the pathway to Princeton. Please specify which step you'd like me to explain."
    else:
        return "I'm sorry, I can provide information on pathways to Princeton and more. How can I assist you further?"

def provide_career_advice():
    return "Here are some career advice tips..."

def provide_test_preparation_tips():
    return "Here are some test preparation tips..."

if __name__ == '__main__':
    app.run(debug=True)