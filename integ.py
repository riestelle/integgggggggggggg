import streamlit as st
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from sympy import latex
from PIL import Image
import pytesseract
import speech_recognition as sr
import pyttsx3

st.set_page_config(page_title="Integral Solver", layout="wide")
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
x = sp.Symbol("x")

# To prevent resizing 
st.markdown(
    """
    <style>
    /* Fix the main container width and prevent resizing */
    .css-18e3th9 {
        max-width: 1200px;  /* change this to your preferred width */
        min-width: 1200px;
        margin: auto;
    }

    .css-1d391kg, .css-1v0mbdj, .stTextInput>div>div>input, textarea, .stTextArea>div>div>textarea {
        font-size: 16px !important;  /* set preferred font size */
    }

    /* Prevent columns from resizing */
    .stColumn > div {
        min-width: 300px;
        max-width: 600px;
    }

    /* Prevent markdown and outputs from resizing */
    .stMarkdown, .stCodeBlock, .stLatex {
        font-size: 16px !important;
    }

    /* Fix graph size */
    .stPyplotChart>div {
        width: 600px !important;  /* figsize width */
        height: 400px !important; /* figsize height */
        margin: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# SPEECH ENGINE SETUP 
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty("rate", 170)


def speak(text):
    """Convert text to speech safely (avoids engine hangups)."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except RuntimeError:
        st.warning("⚠️ Speech engine was busy — skipping voice output.")
    except Exception as e:
        st.error(f"Speech error: {e}")

def listen_for_expression():
    """🎙️ Listen for voice input and convert spoken math into Sympy-compatible text."""
    with sr.Microphone() as source:
        st.info("🎙️ Listening... please speak your function clearly (e.g., 'x squared plus 2x plus 1')")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()

        replacements = {
            "plus": "+",
            "minus": "-",
            "times": "*",
            "multiplied by": "*",
            "divide by": "/",
            "divided by": "/",
            "over": "/",
            "power of": "**",
            "to the power of": "**",
            "squared": "**2",
            "cubed": "**3",
        }

        advanced = {
            "square root of": "sqrt(",
            "squareroot of": "sqrt(",
            "cube root of": "cbrt(",
            "cuberoot of": "cbrt(",
            "sine of": "sin(",
            "sin of": "sin(",
            "cosine of": "cos(",
            "cos of": "cos(",
            "tangent of": "tan(",
            "tan of": "tan(",
            "cotangent of": "cot(",
            "cot of": "cot(",
            "secant of": "sec(",
            "cosecant of": "csc(",
            "csc of": "csc(",
            "arc sine of": "asin(",
            "arc cosine of": "acos(",
            "arc tangent of": "atan(",
            "arc cotangent of": "acot(",
            "arc secant of": "asec(",
            "arc cosecant of": "acsc(",
            "logarithm of": "log(",
            "log of": "log(",
            "natural log of": "ln(",
            "ln of": "ln(",
            "exponential of": "exp(",
            "exponent of": "exp(",
            "e to the power of": "exp(",
        }

        for old, new in {**replacements, **advanced}.items():
            command = command.replace(old, new)

        command = (
            command.replace("√", "sqrt(")
                   .replace("∛", "cbrt(")
                   .replace("^", "**")
        )

        if "sqrt(" in command and not command.endswith(")"):
            command += ")"
        if "cbrt(" in command and not command.endswith(")"):
            command += ")"

        command = command.replace(" ", "")

        st.success(f"🗣️ You said: **{command}**")
        speak("Expression recorded successfully.")
        return command

    except sr.UnknownValueError:
        st.warning("⚠️ Sorry, I didn’t catch that. Please try again.")
        speak("Sorry, I didn’t catch that.")
        return ""
    except sr.RequestError:
        st.error("🚫 Speech recognition service error.")
        speak("There was a problem with the recognition service.")
        return ""

# MAIN UI 
st.title("📐 Integral Solver with OCR & Voice Input")
st.markdown("Upload an image, **speak**, or manually enter a function to compute its integral.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📥 Input Section")

    # OCR  
    ocr_text = ""
    uploaded_file = st.file_uploader("Upload an image of the function (optional)", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        ocr_text = pytesseract.image_to_string(image).strip().replace("\n", "")
        st.write("📄 OCR Extracted Text:")
        st.code(ocr_text)
        st.session_state["ocr_expr"] = ocr_text

    # Voice  
    if st.button("🎙️ Speak Function"):
        voice_text = listen_for_expression()
        if voice_text:
            st.session_state["voice_expr"] = voice_text

    # Text Input 
    default_expr = st.session_state.get("ocr_expr", "") or st.session_state.get("voice_expr", "")
    expr_input = st.text_area("✍️ Function to integrate (in terms of x):", default_expr)

    # Input Help 
    with st.expander("ℹ️ Function Input Help"):
        st.markdown(
            """
            ### 🧮 How to Write Math Expressions (Python-style)
            Use **Python-style syntax** so Sympy can read it correctly.

            **🔹 Basic Rules**
            - Use `**` for powers → `x**2` = \(x^2\)
            - Use `*` for multiplication → `3*x` = \(3x\)
            - Use parentheses for grouping → `(x+1)**2`
            - Use `sqrt(x)` for roots → \(\\sqrt{x}\)

            **🔹 Supported Functions**
            - Trig: `sin(x)`, `cos(x)`, `tan(x)`
            - Inverse Trig: `asin(x)`, `acos(x)`, `atan(x)`
            - Exp/Log: `exp(x)`, `log(x)`
            - Hyperbolic: `sinh(x)`, `cosh(x)`, `tanh(x)`

            **✅ Examples**
            - `x**2 + sin(x) - log(x)`
            - `(x + 2)**3`
            - `exp(x) * cos(x)`

            **⚠️ Common Mistakes**
            - ❌ `x^2` → use `x**2`
            - ❌ `3x` → use `3*x`
            - ❌ `ln(x)` → use `log(x)`
            - ❌ `sinx` → use `sin(x)`
            """
        )

    integral_type = st.radio("Type of Integral:", ["Indefinite", "Definite"])
    a, b = None, None

    if integral_type == "Definite":
        a_input = st.text_input("Lower limit (a):")
        b_input = st.text_input("Upper limit (b):")
        try:
            a, b = float(a_input), float(b_input)
            if a > b:
                a, b = b, a
        except ValueError:
            st.warning("Please enter valid numeric limits for a and b.")
            st.stop()

    use_abs = st.checkbox("Compute total bounded area (ignore sign)", value=False)

# RESULTS & GRAPH 
with col2:
    st.subheader("📊 Integral Result and Graph")

    if st.button("Compute Integral"):
        if not expr_input.strip():
            st.error("Please enter or provide a valid expression.")
            st.stop()

        try:
            expr = sp.sympify(expr_input)
        except sp.SympifyError:
            st.error("Invalid expression syntax.")
            st.stop()

        f = sp.lambdify(x, expr, modules=["numpy"])

        # DEFINITE INTEGRAL 
        if integral_type == "Definite":
            x_vals = np.linspace(a, b, 400)
            y_vals = f(x_vals)

            if use_abs:
                y_vals = np.abs(y_vals)
                integral_numeric = np.trapz(y_vals, x_vals)
                st.markdown("### 🧮 Integral Expression")
                st.latex(r"\int_{" + str(a) + r"}^{" + str(b) + r"} |" + latex(expr) + r"|\,dx")

                # if not integral_numeric.is_integer():
                #     st.markdown("### 🔢 Decimal Approximation")
                #     st.latex(r"\text{Value: } " + f"{integral_numeric:,.6f}")


                speak(f"The total bounded area is approximately {integral_numeric:.2f}")

            else:
                integral_expr = sp.Integral(expr, (x, a, b))
                integral_symbolic = sp.integrate(expr, (x, a, b))
                integral_numeric = float(integral_symbolic.evalf())

                st.markdown("### 🧮 Symbolic Result")
                st.latex(latex(integral_expr) + " = " + latex(integral_symbolic))

                # if not integral_numeric.is_integer():
                #     st.markdown("### 🔢 Decimal Approximation")
                #     st.latex(r"\text{Value: } " + f"{integral_numeric:,.6f}")


                speak(f"The definite integral from {a} to {b} is approximately {integral_numeric:.2f}")

            fig, ax = plt.subplots(figsize=(6, 4))
            # fig, ax = plt.subplots(figsize=(10, 6)) #remove comment and comment the one above if you want to make it resizable/bigger
            ax.plot(x_vals, y_vals, label=f'$f(x) = {latex(expr)}$', color='blue', linewidth=2)
            ax.axhline(0, color='black', linewidth=1.2)
            ax.axvline(0, color='black', linewidth=1.0, linestyle=':')

            ax.axvline(a, color='red', linestyle='--', linewidth=1.5, label=f'$x = {a}$')
            ax.axvline(b, color='red', linestyle='--', linewidth=1.5, label=f'$x = {b}$')

            ax.fill_between(
                x_vals, y_vals, 0,
                where=(x_vals >= a) & (x_vals <= b),
                interpolate=True,
                color='skyblue', alpha=0.5
            )

            ax.set_title("Function Plot with Bounded Area", fontsize=16)
            ax.set_xlabel("x", fontsize=14)
            ax.set_ylabel("f(x)", fontsize=14)
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig, use_container_width=False)
            #st.pyplot(fig) #use this instead of the one above if you want to make it resizable


        # INDEFINITE INTEGRAL 
        else:
            integral_symbolic = sp.integrate(expr, x)
            st.markdown("### 🧮 Symbolic Result")
            st.latex(r"\int " + latex(expr) + r"\, dx = " + latex(integral_symbolic) + r" + C")
            
            speak("The indefinite integral has been computed successfully.")

            x_vals = np.linspace(-10, 10, 400)
            f_vals = np.array([f(val) for val in x_vals])
            F = sp.lambdify(x, integral_symbolic, modules=["numpy"])
            F_vals = np.array([F(val) for val in x_vals])

            fig, ax = plt.subplots(figsize=(6, 4))
            # fig, ax = plt.subplots(figsize=(10,6)) #remove comment and comment the one above if you want to make it resizable/bigger
            ax.plot(x_vals, f_vals, label=r"$f(x)$", color="blue", linewidth=2)
            ax.plot(x_vals, F_vals, label=r"$\int f(x)\,dx + C$", color="green", linestyle="--", linewidth=2)

            ax.axhline(0, color="black", linewidth=1.2)
            ax.axvline(0, color="black", linestyle=":", linewidth=1.0)
            ax.set_title("Function and Its Indefinite Integral", fontsize=16)
            ax.set_xlabel("x", fontsize=14)
            ax.set_ylabel("Value", fontsize=14)
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig, use_container_width=False)
            # st.pyplot(fig) #use this instead of the one above if you want to make it resizable


