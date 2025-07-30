from fasthtml.common import *
from database import add_word, remove_word, get_all_words, get_active_words
from anthropic import Anthropic
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

# Initialize Anthropic client
anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# FastHTML app setup
app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'),
        Style('''
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: #ffffff;
                color: #37352f;
                line-height: 1.5;
                min-height: 100vh;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .header {
                text-align: center;
                margin-bottom: 3rem;
                padding: 2rem 0;
            }
            
            h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                color: #37352f;
            }
            
            .subtitle {
                color: #787774;
                font-size: 1.125rem;
            }
            
            .nav {
                display: flex;
                gap: 1rem;
                justify-content: center;
                margin: 2rem 0;
                border-bottom: 1px solid #e9e9e7;
                padding-bottom: 1rem;
            }
            
            .nav-link {
                padding: 0.5rem 1rem;
                text-decoration: none;
                color: #37352f;
                font-weight: 500;
                border-radius: 6px;
                transition: all 0.2s;
            }
            
            .nav-link:hover {
                background: #f4f4f2;
            }
            
            .nav-link.active {
                background: #37352f;
                color: white;
            }
            
            .card {
                background: #ffffff;
                border: 1px solid #e9e9e7;
                border-radius: 8px;
                padding: 2rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            }
            
            .word-list {
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
                margin: 1.5rem 0;
            }
            
            .word-tag {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: #f4f4f2;
                border-radius: 6px;
                font-size: 0.875rem;
            }
            
            .remove-btn {
                background: none;
                border: none;
                color: #eb5757;
                cursor: pointer;
                font-size: 1.25rem;
                line-height: 1;
                padding: 0;
                margin-left: 0.25rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            .input-group {
                display: flex;
                gap: 0.75rem;
            }
            
            input[type="text"] {
                flex: 1;
                padding: 0.75rem 1rem;
                border: 1px solid #e9e9e7;
                border-radius: 6px;
                font-size: 1rem;
                font-family: inherit;
                transition: border-color 0.2s;
            }
            
            input[type="text"]:focus {
                outline: none;
                border-color: #37352f;
            }
            
            .btn {
                padding: 0.75rem 1.5rem;
                background: #37352f;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 1rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                font-family: inherit;
            }
            
            .btn:hover {
                background: #2f2f2f;
                transform: translateY(-1px);
            }
            
            .btn-secondary {
                background: #f4f4f2;
                color: #37352f;
            }
            
            .btn-secondary:hover {
                background: #e9e9e7;
            }
            
            .quiz-card {
                text-align: center;
                padding: 3rem 2rem;
            }
            
            .quiz-word {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 2rem;
                color: #37352f;
            }
            
            .quiz-options {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .option-btn {
                width: 100%;
                padding: 1.25rem;
                text-align: left;
                background: #f4f4f2;
                border: 2px solid transparent;
                border-radius: 8px;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .option-btn:hover {
                background: #e9e9e7;
                border-color: #37352f;
            }
            
            .option-btn.correct {
                background: #d1f4e0;
                border-color: #27ae60;
            }
            
            .option-btn.incorrect {
                background: #ffe0e0;
                border-color: #eb5757;
            }
            
            .stats {
                display: flex;
                justify-content: center;
                gap: 3rem;
                margin: 2rem 0;
            }
            
            .stat {
                text-align: center;
            }
            
            .stat-value {
                font-size: 2rem;
                font-weight: 700;
                color: #37352f;
            }
            
            .stat-label {
                color: #787774;
                font-size: 0.875rem;
            }
            
            .message {
                padding: 1rem;
                border-radius: 6px;
                margin: 1rem 0;
                text-align: center;
            }
            
            .message.success {
                background: #d1f4e0;
                color: #27ae60;
            }
            
            .message.error {
                background: #ffe0e0;
                color: #eb5757;
            }
            
            .congrats {
                text-align: center;
                padding: 3rem;
            }
            
            .congrats h2 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            
            .loading {
                display: flex;
                justify-content: center;
                padding: 2rem;
                color: #787774;
            }
        ''')
    )
)

# Session state
quiz_state = {
    'words_remaining': [],
    'current_word': None,
    'streak': 0,
    'correct_answers': 0,
    'total_words': 0
}

def reset_quiz():
    words = get_active_words()
    quiz_state['words_remaining'] = [w.word for w in words]
    quiz_state['streak'] = 0
    quiz_state['correct_answers'] = 0
    quiz_state['total_words'] = len(words)
    quiz_state['current_word'] = None

def get_quiz_options(word):
    """Get multiple choice options from Claude API"""
    try:
        message = anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7,
            system="You are a vocabulary tutor helping students prepare for the 11+ exam. Generate challenging but fair multiple choice options.",
            messages=[{
                "role": "user",
                "content": f"""Generate 3 different definitions or uses for the word "{word}" for a multiple choice quiz.
                
                The first one must be the CORRECT definition/use.
                The other two should be plausible but incorrect alternatives that would make the quiz reasonably challenging.
                
                Return your response as a JSON object with this exact structure:
                {{
                    "options": [
                        "correct definition or use",
                        "plausible but incorrect option 1",
                        "plausible but incorrect option 2"
                    ]
                }}
                
                Make sure the options are of similar length and complexity."""
            }]
        )
        
        # Parse the response
        content = message.content[0].text
        # Extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data['options']
        else:
            # Fallback options
            return [
                f"The correct definition of {word}",
                f"An incorrect definition of {word} (option 1)",
                f"An incorrect definition of {word} (option 2)"
            ]
    except Exception as e:
        print(f"Error getting options from Claude: {e}")
        # Fallback options
        return [
            f"The correct definition of {word}",
            f"An incorrect definition of {word} (option 1)", 
            f"An incorrect definition of {word} (option 2)"
        ]

@rt('/')
def get():
    return Div(
        Div(
            H1("Ronin's Vocab"),
            P("11+ Exam Vocabulary Practice Tool", cls='subtitle'),
            cls='header'
        ),
        Div(
            A('Quiz', href='/quiz', cls='nav-link'),
            A('Config', href='/config', cls='nav-link'),
            cls='nav'
        ),
        Div(
            H2('Welcome!', style='text-align: center; margin: 3rem 0;'),
            P('Start with the Quiz to practice vocabulary, or go to Config to manage your word list.',
              style='text-align: center; color: #787774; font-size: 1.125rem;'),
            cls='container'
        ),
        cls='container'
    )

@rt('/config')
def get():
    words = get_all_words()
    
    return Div(
        Div(
            H1("Ronin's Vocab"),
            P("11+ Exam Vocabulary Practice Tool", cls='subtitle'),
            cls='header'
        ),
        Div(
            A('Quiz', href='/quiz', cls='nav-link'),
            A('Config', href='/config', cls='nav-link active'),
            cls='nav'
        ),
        Div(
            Div(
                H2('Manage Vocabulary'),
                Div(
                    Div(
                        Input(type='text', id='new-word', placeholder='Enter a new word...', 
                              hx_trigger='keyup[key=="Enter"]',
                              hx_post='/add-word',
                              hx_target='#word-list',
                              hx_include='#new-word'),
                        Button('Add Word', cls='btn',
                               hx_post='/add-word',
                               hx_target='#word-list',
                               hx_include='#new-word'),
                        cls='input-group'
                    ),
                    cls='form-group'
                ),
                Div(
                    *[Div(
                        word.word,
                        Button('×', cls='remove-btn',
                               hx_delete=f'/remove-word/{word.id}',
                               hx_target='#word-list',
                               hx_confirm=f'Remove "{word.word}" from the list?'),
                        cls='word-tag'
                    ) for word in words],
                    id='word-list',
                    cls='word-list'
                ),
                P(f'Total words: {len(words)}', style='color: #787774; text-align: center;'),
                cls='card'
            ),
            cls='container'
        )
    )

@rt('/add-word', methods=['POST'])
async def post(request):
    form = await request.form()
    new_word = form.get('new-word', '').strip().lower()
    
    if new_word:
        add_word(new_word)
    
    words = get_all_words()
    return Div(
        *[Div(
            word.word,
            Button('×', cls='remove-btn',
                   hx_delete=f'/remove-word/{word.id}',
                   hx_target='#word-list',
                   hx_confirm=f'Remove "{word.word}" from the list?'),
            cls='word-tag'
        ) for word in words],
        id='word-list',
        cls='word-list'
    ), Script('document.getElementById("new-word").value = "";')

@rt('/remove-word/{word_id}', methods=['DELETE'])
def delete(word_id: int):
    remove_word(word_id)
    words = get_all_words()
    
    return Div(
        *[Div(
            word.word,
            Button('×', cls='remove-btn',
                   hx_delete=f'/remove-word/{word.id}',
                   hx_target='#word-list',
                   hx_confirm=f'Remove "{word.word}" from the list?'),
            cls='word-tag'
        ) for word in words],
        id='word-list',
        cls='word-list'
    )

@rt('/quiz')
def get():
    if not quiz_state['words_remaining']:
        reset_quiz()
    
    return Div(
        Div(
            H1("Ronin's Vocab"),
            P("11+ Exam Vocabulary Practice Tool", cls='subtitle'),
            cls='header'
        ),
        Div(
            A('Quiz', href='/quiz', cls='nav-link active'),
            A('Config', href='/config', cls='nav-link'),
            cls='nav'
        ),
        Div(
            Div(
                Div(
                    Div(f'Streak: {quiz_state["streak"]}', cls='stat-value'),
                    Div('Current Streak', cls='stat-label'),
                    cls='stat'
                ),
                Div(
                    Div(f'{quiz_state["correct_answers"]}/{quiz_state["total_words"]}', cls='stat-value'),
                    Div('Progress', cls='stat-label'),
                    cls='stat'
                ),
                cls='stats'
            ),
            Div(id='quiz-content', hx_get='/quiz/next', hx_trigger='load'),
            cls='container'
        )
    )

@rt('/quiz/next')
def get():
    if not quiz_state['words_remaining']:
        return Div(
            Div(
                H2('🎉 Congratulations!'),
                P(f'You completed all {quiz_state["total_words"]} words!'),
                P(f'Final streak: {quiz_state["streak"]}'),
                Button('Start Again', cls='btn', onclick='window.location.href="/quiz"'),
                cls='congrats'
            ),
            cls='card quiz-card'
        )
    
    # Pick a random word
    word = random.choice(quiz_state['words_remaining'])
    quiz_state['current_word'] = word
    
    return Div(
        Div('Loading question...', cls='loading'),
        cls='card quiz-card',
        hx_get=f'/quiz/question/{word}',
        hx_trigger='load',
        hx_swap='outerHTML'
    )

@rt('/quiz/question/{word}')
def get(word: str):
    options = get_quiz_options(word)
    
    # Shuffle options but remember correct answer position
    correct_answer = options[0]
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)
    correct_index = shuffled_options.index(correct_answer)
    
    return Div(
        Div(word, cls='quiz-word'),
        Div(
            *[Button(
                option,
                cls='option-btn',
                hx_post=f'/quiz/answer',
                hx_vals=json.dumps({
                    'word': word,
                    'answer_index': i,
                    'correct_index': correct_index
                }),
                hx_target='#quiz-content',
                hx_swap='innerHTML'
            ) for i, option in enumerate(shuffled_options)],
            cls='quiz-options'
        ),
        cls='card quiz-card'
    )

@rt('/quiz/answer', methods=['POST'])
async def post(request):
    form = await request.form()
    data = json.loads(form.get('hx-vals', '{}'))
    
    word = data.get('word')
    answer_index = data.get('answer_index')
    correct_index = data.get('correct_index')
    
    is_correct = answer_index == correct_index
    
    if is_correct:
        quiz_state['streak'] += 1
        quiz_state['correct_answers'] += 1
        quiz_state['words_remaining'].remove(word)
        message = Div('Correct! Well done!', cls='message success')
    else:
        quiz_state['streak'] = 0
        message = Div('Incorrect. Keep trying!', cls='message error')
    
    return Div(
        message,
        Div(
            Button('Next Word', cls='btn', hx_get='/quiz/next', hx_target='#quiz-content'),
            style='text-align: center; margin-top: 1rem;'
        )
    )

@rt('/api/init')
def get():
    reset_quiz()
    return {'status': 'initialized'}

if __name__ == '__main__':
    serve()