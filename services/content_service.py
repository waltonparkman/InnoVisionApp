from services.ai_service import adapt_content_difficulty

def get_personalized_content(user, course):
    # Dummy content for demonstration
    content = {
        'visual': {
            'easy': 'Simple diagrams and infographics',
            'medium': 'Detailed flowcharts and mind maps',
            'hard': 'Complex data visualizations and interactive graphics'
        },
        'auditory': {
            'easy': 'Basic audio lectures with simple concepts',
            'medium': 'In-depth podcast-style lessons',
            'hard': 'Advanced audio discussions with expert interviews'
        },
        'kinesthetic': {
            'easy': 'Simple hands-on exercises',
            'medium': 'Interactive simulations',
            'hard': 'Complex real-world projects'
        },
        'reading/writing': {
            'easy': 'Short articles with key concepts',
            'medium': 'Comprehensive study guides',
            'hard': 'Academic papers and in-depth analysis'
        }
    }

    # Get user's learning style and adapt difficulty based on performance
    learning_style = user.learning_style or 'visual'  # Default to visual if not set
    user_course = next((uc for uc in user.user_courses if uc.course_id == course.id), None)
    difficulty = adapt_content_difficulty(user_course.progress if user_course else 0)

    return content[learning_style][difficulty]
