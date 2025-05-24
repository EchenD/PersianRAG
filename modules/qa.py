# ─────────────────────────────────
# IMPORTS
# ─────────────────────────────────
import re
import random
from typing import Union, Tuple, List, Dict, Literal, TypedDict

# ─────────────────────────────────
# TYPE DEFINITIONS
# ─────────────────────────────────
class InteractionResponse(TypedDict):
    user: str
    assistant: str

# Represents the successful return type for handler functions
SuccessfulHandlerReturn = Tuple[Literal[True], InteractionResponse]
# Represents the return type when no match is found
FailedHandlerReturn = Literal[False]
# Combined return type for handler functions
HandlerReturn = Union[SuccessfulHandlerReturn, FailedHandlerReturn]

# ─────────────────────────────────
# GREETING AND FAREWELL DETECTION
# ─────────────────────────────────

# Define categories for different types of greetings and social interactions
# Each category contains a list of regex patterns and corresponding responses.
interaction_categories = [
    {
        "name": "general_salutation",
        "patterns": [
            r"\bسلام\b", r"\bدرود\b", r"\bسلام\s+علیکم\b", r"\bسام\s+علیکم\b", r"\bسام\s+علیک\b",
            r"\bسلام\s+دوست\s+عزیز\b", r"\bسلامتی\b", r"\bسلام\s+بر\s+همگی\b", r"\bدرود\s+بر\s+شما\b",
            r"\bسلام\s+و\s+عرض\s+ادب\b", r"\bسلام\s+بر\s+شما\s+عزیزان\b", r"\bبا\s+سلام\b",
            r"\bعلیک\s+سلام\b", r"\bسلام\s+خدمت\s+شما\b",
        ],
        "responses": [
            "سلام! چطور می‌توانم به شما کمک کنم؟",
            "درود بر شما! چه کمکی از دست من ساخته است؟",
            "سلام! روز خوبی داشته باشید. بفرمایید.",
            "سلام! خوشحالم که با شما صحبت می‌کنم. در خدمتم.",
            "علیک سلام! بفرمایید، آماده کمک هستم.",
        ]
    },
    {
        "name": "time_based_greeting",
        "patterns": [
            r"\bصبح\s+بخیر\b", r"\bظهر\s+بخیر\b", r"\bعصر\s+بخیر\b", r"\bشب\s+بخیر\b",
            r"\bوقت\s+بخیر\b",
            r"\bصبح\s+شما\s+بخیر\b", r"\bظهر\s+شما\s+بخیر\b", r"\bعصر\s+شما\s+بخیر\b", r"\bشب\s+شما\s+بخیر\b",
            r"\bصبح\s+بخیر\s+بر\s+شما\s+عزیزان\b", r"\bعصر\s+بخیر\s+بر\s+شما\s+عزیزان\b",
            r"\bشب\s+بخیر\s+بر\s+شما\s+عزیزان\b",
            r"\bروز\s+بخیر\b",
        ],
        "responses_map": { # Using a map for more specific responses based on time
            "صبح": "صبح بخیر! روزتان پر از انرژی و موفقیت.",
            "ظهر": "ظهر بخیر! امیدوارم روز خوبی را سپری کرده باشید.",
            "عصر": "عصر بخیر! چطور می‌توانم در این ساعات به شما یاری رسانم؟",
            "شب": "شب بخیر! امیدوارم شب آرامی داشته باشید.",
            "وقت": "وقت بخیر! در خدمتم.",
            "روز": "روز شما هم بخیر.",
        },
        "default_time_response": "وقت شما بخیر! چطور می توانم کمکتان کنم؟"
    },
    {
        "name": "how_are_you",
        "patterns": [
            r"\bچه\s+خبر\b", r"\bحالت\s+چطوره\b", r"\bخوبی\b", r"\bچطوری\b",
            r"\bاوضاع\s+چطوره\b", r"\bچه\s+خبر\s+خوبی\s+دارید\b", r"\bهمه\s+چی\s+خوبه\b",
            r"\bدر\s+چه\s+حالی\b",
        ],
        "responses": [
            "ممنون، همه چیز خوب است. شما چطورید؟ آماده‌ام به سوالات شما پاسخ دهم.",
            "خوبم، متشکرم که پرسیدید. چطور می‌توانم به شما کمک کنم؟",
            "الحمدلله خوبم. در خدمت شما هستم.",
            "همه چیز مرتب است، ممنون. بفرمایید سوالتان را.",
        ]
    },
    {
        "name": "welcome",
        "patterns": [
            r"\bخوش\s+آمدید\b", r"\bخوش\s+آمدی\b",
            r"\bخوش\s+آمدید\s+به\s+خدمت\b",
        ],
        "responses": [
            "خوش آمدید! امیدوارم تجربه خوبی در استفاده از این سیستم داشته باشید.",
            "خیلی خوش آمدید! در خدمت شما هستم.",
            "خوش آمدید! باعث افتخار است که بتوانم کمکتان کنم.",
        ]
    },
    {
        "name": "farewell",
        "patterns": [
            r"\bخداحافظ\b", r"\bخدانگهدار\b", r"\bبه\s+امید\s+دیدار\b", r"\bفعلا\b",
            r"\bخدافظ\b", r"\bبای\b", r"\bروز\s+خوش\b", r"\bشب\s+خوش\b",
            r"\bتا\s+بعد\b", r"\bمیبینمت\b",
        ],
        "responses": [
            "خداحافظ! امیدوارم دوباره شما را ببینم.",
            "خدانگهدار! مراقب خودتان باشید.",
            "به امید دیدار! موفق باشید.",
            "فعلا خدانگهدار!",
            "روز/شب خوشی را برایتان آرزومندم.",
        ]
    },
    {
        "name": "politeness_acknowledgement", # e.g., "Don't be tired"
        "patterns": [
            r"\bخسته\s+نباشید\b",
            r"\bخوش\s+بختی\s+باشید\b", # Can be a wish, sometimes used in parting
            r"\bخوش\s+حال\s+شدم\s+از\s+دیدارتان\b",
        ],
        "responses": [
            "سلامت باشید! باعث خوشحالی است که توانستم کمک کنم.",
            "ممنون از لطفتان! همچنین برای شما آرزوی موفقیت دارم.",
            "زنده باشید! من هم از تعامل با شما خوشحال شدم.",
        ]
    }
]

def handle_greeting(user_input: str) -> HandlerReturn:
    """
    Handles various Persian greetings, farewells, and common social interactions.

    Args:
        user_input (str): The user's input string.

    Returns:
        Union[Tuple[Literal[True], InteractionResponse], Literal[False]]: 
        A tuple (True, response_dict) if a greeting is detected, 
        otherwise False.
    """
    normalized_input = user_input.strip() # Basic normalization

    for category in interaction_categories:
        for pattern in category["patterns"]:
            match = re.search(pattern, normalized_input, flags=re.IGNORECASE)
            if match:
                reply = ""
                if category["name"] == "time_based_greeting":
                    # More specific response for time-based greetings
                    if "صبح" in match.group(0):
                        reply = category["responses_map"]["صبح"]
                    elif "ظهر" in match.group(0):
                        reply = category["responses_map"]["ظهر"]
                    elif "عصر" in match.group(0):
                        reply = category["responses_map"]["عصر"]
                    elif "شب" in match.group(0) and "خوش" not in match.group(0): # شب بخیر vs شب خوش (farewell)
                        reply = category["responses_map"]["شب"]
                    elif "وقت" in match.group(0):
                         reply = category["responses_map"]["وقت"]
                    elif "روز" in match.group(0):
                         reply = category["responses_map"]["روز"]
                    else:
                        reply = category["default_time_response"]
                elif category["name"] == "farewell":
                    # Adjust farewell if it's time specific
                    if "روز خوش" in match.group(0):
                        reply = "روز خوشی داشته باشید! خدانگهدار."
                    elif "شب خوش" in match.group(0):
                        reply = "شب خوشی داشته باشید! خدانگهدار."
                    else:
                        reply = random.choice(category["responses"])
                else:
                    reply = random.choice(category["responses"])
                
                return True, reply
    
    return False

# ─────────────────────────────────
# META-QUESTION DETECTION
# ─────────────────────────────────

def handle_meta_question(user_input: str) -> HandlerReturn:
    """
    Handles meta-related questions in Persian by redirecting the conversation.

    Args:
        user_input (str): The user's input string.

    Returns:
        Union[Tuple[Literal[True], InteractionResponse], Literal[False]]: 
        A tuple (True, response_dict) if a meta-question is detected, 
        otherwise False.
    """
    normalized_input = user_input.strip()

    # Comprehensive list of regex patterns for meta-related questions
    meta_patterns = [
        # Who made you / Who are you
        r"\b(چه\s+کسی|کی)\s+(شما\s+را|تو\s+رو|تورو)\s+(ساخته|درست\s+کرده)\s*(است|؟|\.)*\b",
        r"\b(شما|تو)\s+(کی|چی)\s+(هستی|هستید)\s*(؟|\.)*\b",
        r"\bسازنده\s*(ی|‌)\s*(شما|تو)\s+(کیست|کیه)\s*(؟|\.)*\b",
        r"\bتوسعه\s+دهنده\s*(ی|‌)\s*(شما|تو)\s+(کیست|کیه)\s*(؟|\.)*\b",
        r"\bخالق\s*(شما|تو)\s+(کیست|کیه)\s*(؟|\.)*\b",
        
        # What is your name
        r"\bاسم\s*(ت|شما|تو)\s+(چیست|چیه)\s*(؟|\.)*\b",
        r"\bنام\s*(ت|شما|تو)\s+(چیست|چیه)\s*(؟|\.)*\b",
        r"\bخودت(و|)\s+معرفی\s+کن\b",
        r"\bمی\s*(تونم|شه)\s+اسمت(و|)\s+بدونم\b",

        # Which company made you
        r"\b(کدام|چه)\s+شرکتی\s+(شما\s+را|تو\s+رو|تورو)\s+(ساخته|توسعه\s+داده)\s*(است|؟|\.)*\b",
        r"\bتولید\s+شده\s+توسط\s+(کدام|چه)\s+شرکتی\s*(هستید|هستی)\s*(؟|\.)*\b",
        r"\bمالک\s*(شما|تو)\s+(کیست|کیه|کدوم\s+شرکته)\s*(؟|\.)*\b",

        # How old are you
        r"\bسن\s*(شما|تو)\s+(چند|چقدر)\s*(است|ه|؟|\.)*\b",
        r"\b(چند\s+سالته|چند\s+سالتونه|چند\s+سال\s+دارید)\s*(؟|\.)*\b",
        
        # Where are you from
        r"\b(از\s+کجا|اهل\s+کجا)\s+(هستی|هستید)\s*(؟|\.)*\b",
        r"\b(شما|تو)\s+مال\s+کجایی\b",

        # General "about you"
        r"\bدر\s+مورد\s+خودت\s+بگو\b",
        r"\bکمی\s+از\s+خودت\s+بگو\b",
    ]

    for pattern in meta_patterns:
        if re.search(pattern, normalized_input, flags=re.IGNORECASE):
            redirect_replies = [
                "من یک دستیار هوش مصنوعی هستم که برای کمک به شما در زمینه اطلاعات موجود در اسناد شرکت طراحی شده‌ام. لطفاً سوال خود را در مورد محتوای مستندات بپرسید.",
                "تمرکز من بر ارائه اطلاعات از مستندات شرکت است. چطور می‌توانم در این زمینه به شما کمک کنم؟",
                "اطلاعات مربوط به منشا و ساختار من خارج از محدوده کاری تعریف شده است. لطفاً سوالات خود را به محتوای اسناد معطوف کنید.",
                "هدف من کمک به شما با اطلاعات درون سازمانی است. سوال شما در مورد اسناد چیست؟",
                "بیایید روی وظیفه اصلی تمرکز کنیم: پاسخ به سوالات شما از مستندات شرکت. بفرمایید."
            ]
            reply = random.choice(redirect_replies)
            return True, reply

    return False


# ─────────────────────────────────
# EXAMPLE USAGE (for testing)
# ─────────────────────────────────
if __name__ == "__main__":
    test_inputs_greetings = [
        "سلام", "سلام علیکم", "صبح بخیر", "حالت چطوره؟", "خوبی عزیزم؟",
        "خداحافظ", "خدانگهدارتون", "خسته نباشید استاد", "وقت بخیر قربان",
        "سام علیک", "چه خبر؟ خوبی داری؟", "سلام و عرض ادب خدمت شما", "بای", "فعلا",
        "درود بر شما دوست گرامی", "خوش آمدید به سیستم ما"
    ]

    test_inputs_meta = [
        "تو کی هستی؟", "اسمت چیه؟", "چه کسی شما را ساخته است؟", "سازنده تو کیه؟",
        "کدوم شرکت تو رو توسعه داده؟", "چند سالته؟", "مالک شما کیست", "از کجا اومدی",
        "می‌توانید خودتان را معرفی کنید؟", "کمی از خودت بگو بینم"
    ]

    print("--- Testing Greetings ---")
    for text in test_inputs_greetings:
        result = handle_greeting(text)
        if result:
            print(f"Input: {text}\nResponse: {result[1]['assistant']}\n")
        else:
            print(f"Input: {text}\nNo greeting detected.\n")

    print("\n--- Testing Meta-Questions ---")
    for text in test_inputs_meta:
        result = handle_meta_question(text)
        if result:
            print(f"Input: {text}\nResponse: {result[1]['assistant']}\n")
        else:
            print(f"Input: {text}\nNo meta-question detected.\n")
            
    # Test non-matching cases
    print("\n--- Testing Non-Matching Inputs ---")
    non_matching_inputs = [
        "قیمت محصول ایکس چنده؟",
        "چطور میتونم فایلم رو آپلود کنم؟",
        "این یک جمله معمولی است."
    ]
    for text in non_matching_inputs:
        result_greeting = handle_greeting(text)
        result_meta = handle_meta_question(text)
        print(f"Input: {text}")
        print(f"  Greeting Handler: {'Detected' if result_greeting else 'Not Detected'}")
        print(f"  Meta Handler: {'Detected' if result_meta else 'Not Detected'}\n")
