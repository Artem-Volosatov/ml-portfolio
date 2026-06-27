from pathlib import Path
import streamlit as st
import torch
import json
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Project structure setup
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = str(BASE_DIR / "model")
CLASSES_PATH = str(BASE_DIR / "data" / "classes.json")
DESCRIPTIONS_PATH = str(BASE_DIR / "data" / "category_descriptions.csv")

THRESHOLD = 0.25


def colored_progress_bar(prob, color):
    st.markdown(
        f"""
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 5px; height: 10px; margin: 10px 0;">
            <div style="width: {prob*100}%; background-color: {color}; height: 10px; border-radius: 5px;"></div>
        </div>
        """,
        unsafe_allow_html=True
    )


@st.cache_resource
def load_resources():
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_PATH, local_files_only=True)
    model.eval()

    with open(CLASSES_PATH, "r", encoding="utf-8") as f:
        idx2tag = json.load(f)

    df_desc = pd.read_csv(DESCRIPTIONS_PATH)
    tag2name = dict(zip(df_desc['tag'], df_desc['name']))
    tag2desc = dict(zip(df_desc['tag'], df_desc['description']))

    return tokenizer, model, idx2tag, tag2name, tag2desc


EXAMPLES = {
    "Mathematical Physics": {
        "title": "The Semiclassical Einstein-Klein-Gordon System: Asymptotic Analysis of Minkowski Spacetime",
        "abstract": """We establish the linear instability of the semiclassical Einstein-Klein-Gordon system linearised about the Minkowski vacuum spacetime. The proof relies on formulating a forcing problem for both metric and state perturbations within the space of past-compact sections. This geometric framework admits a unique tensor decomposition which, in conjunction with the quantum Møller operator, enables the decoupling of the linearised system into two distinct Cauchy problems. Consequently, the metric perturbations are shown to be governed by a higher-order, nonlocal hyperbolic partial differential equation. By relegating the nonlocal contributions to subleading order, we establish the well-posedness of this forcing problem. Furthermore, we provide a rigorous asymptotic analysis for physically admissible choices of the renormalisation constants. We prove that the system exhibits a late-time linear instability: the metric perturbations grow exponentially, bounded strictly by a universal scale H, thereby indicating a quantum backreaction-driven transition toward a de Sitter cosmological spacetime. Provided the parameters governing the system are restricted to a physically relevant regime, this universal scale is compatible with the measured expansion of our universe."""
    },
    "Category Theory": {
        "title": "On the universality of multiexcisive functors",
        "abstract": """We provide a multiplicative classification of polynomial endofunctors on spectra in terms of their Mackey functors of cross--effects. More precisely, we prove that various categories of multivariable excisive functors from spectra to spectra are symmetric monoidally equivalent to the corresponding variants of spectral Mackey functors. The symmetric monoidal structures appearing here are the Day convolutions on both sides, and the Mackey functors we consider involve variations on the category of finite sets and surjections. The method is first to introduce certain multivariable functors we call subdiagonal functors. By considering them all at once using parametrised category theory, we prove inductively that they all admit Mackey functor descriptions as symmetric monoidal categories, endowing them with a universal property along the way. In particular, specialising this to univariate functors gives a new proof and strengthening of Glasman's result about d-excisive endofunctors on spectra. As application of our perspective, we prove a ``Segal conjecture'' in the context of Goodwillie calculus when d is a prime number."""
    },
    "Machine Learning": {
        "title": "Learning from Equivalence Queries, Revisited",
        "abstract": """Modern machine learning systems, such as generative models and recommendation systems, often evolve through a cycle of deployment, user interaction, and periodic model updates. This differs from standard supervised learning frameworks, which focus on loss or regret minimization over a fixed sequence of prediction tasks. Motivated by this setting, we revisit the classical model of learning from equivalence queries, introduced by Angluin (1988). In this model, a learner repeatedly proposes hypotheses and, when a deployed hypothesis is inadequate, receives a counterexample. Under fully adversarial counterexample generation, however, the model can be overly pessimistic. In addition, most prior work assumes a \\emph{full-information} setting, where the learner also observes the correct label of the counterexample, an assumption that is not always natural. We address these issues by restricting the environment to a broad class of less adversarial counterexample generators, which we call \\emph{symmetric}. Informally, such generators choose counterexamples based only on the symmetric difference between the hypothesis and the target. This class captures natural mechanisms such as random counterexamples (Angluin and Dohrn, 2017; Bhatia, 2021; Chase, Freitag, and Reyzin, 2024), as well as generators that return the simplest counterexample according to a prescribed complexity measure. Within this framework, we study learning from equivalence queries under both full-information and bandit feedback. We obtain tight bounds on the number of learning rounds in both settings and highlight directions for future work. Our analysis combines a game-theoretic view of symmetric adversaries with adaptive weighting methods and minimax arguments."""
    },
    "Image and Video Processing": {
        "title": "4D Vessel Reconstruction for Benchtop Thrombectomy Analysis",
        "abstract": """Introduction: Mechanical thrombectomy can cause vessel deformation and procedure-related injury. Benchtop models are widely used for device testing, but time-resolved, full-field 3D vessel-motion measurements remain limited. Methods: We developed a nine-camera, low-cost multi-view workflow for benchtop thrombectomy in silicone middle cerebral artery phantoms (2160p, 20 fps). Multi-view videos were calibrated, segmented, and reconstructed with 4D Gaussian Splatting. Reconstructed point clouds were converted to fixed-connectivity edge graphs for region-of-interest (ROI) displacement tracking and a relative surface-based stress proxy. Stress-proxy values were derived from edge stretch using a Neo-Hookean mapping and reported as comparative surface metrics. A synthetic Blender pipeline with known deformation provided geometric and temporal validation. Results: In synthetic bulk translation, the stress proxy remained near zero for most edges (median 0 MPa; 90th percentile 0.028 MPa), with sparse outliers. In synthetic pulling (1-5 mm), reconstruction showed close geometric and temporal agreement with ground truth, with symmetric Chamfer distance of 1.714-1.815 mm and precision of 0.964-0.972 at mm. In preliminary benchtop comparative trials (one trial per condition), cervical aspiration catheter placement showed higher max-median ROI displacement and stress-proxy values than internal carotid artery terminus placement. Conclusion: The proposed protocol provides standardized, time-resolved surface kinematics and comparative relative displacement and stress proxy measurements for thrombectomy benchtop studies. The framework supports condition-to-condition comparisons and methods validation, while remaining distinct from absolute wall-stress estimation. Implementation code and example data are available at this https URL."""
    },
    "Physics and Society": {
        "title": "Emergence of cooperation in nonlinear higher-order public goods games",
        "abstract": """Evolutionary game theory has provided substantial contributions to explain the emergence of cooperation under unfavourable conditions in ecology, economics, and the social sciences. Recently, inspired by newly available empirical evidence on group interactions, higher-order networks have emerged as a natural framework to properly encode multiplayer games in structured populations. Here, we study the emergence of cooperation in a nonlinear public goods game (PGG) on hypergraphs, where collective reinforcement captures the synergistic or discounting effect associated with each additional cooperator. In well-mixed populations, single-order PGGs, where all games have the same number of players, display a change in the nature of transition from continuous to discontinuous depending on the exact form of nonlinearity. By contrast, mixed-order PGGs, where games with different number of players coexist, exhibit a richer dynamical regime wherein a state of active coexistence of bistability and cooperation can arise. We further find that scale-free hypergraphs promote cooperation, highlighting the crucial role played by both the initial placement of cooperators and the presence of hyperdegree correlations. Overall, our results provide a comprehensive characterization of nonlinear PGGs on hypergraphs and open up new avenues for richer models of evolutionary dynamics of multiplayer interactions on structured populations."""
    }
}

# UI Configuration
st.set_page_config(page_title="arXiv Paper Classifier",
                   page_icon="🧠", layout="wide")

with st.sidebar:
    st.header("📌 Project Info")
    st.info("This is an NLP-based tool that classifies scientific papers into arXiv categories using a fine-tuned Transformer model.")

    st.divider()

    st.header("🚀 Quick Examples")
    st.write("Click an example to fill the inputs:")

    for ex_name, ex_data in EXAMPLES.items():
        if st.button(ex_name, use_container_width=True):
            st.session_state['title_input'] = ex_data['title']
            st.session_state['abstract_input'] = ex_data['abstract']
            st.rerun()

    st.divider()
    st.markdown(
        "Developed by [Artem Volosatov](https://github.com/Artem-Volosatov)")

st.title("arXiv Paper Classifier")
st.write("Enter the paper title and abstract to find the most relevant categories.")

try:
    tokenizer, model, idx2tag, tag2name, tag2desc = load_resources()
except Exception as e:
    st.error(f"Error loading resources: {e}")
    st.stop()

# Input section
title = st.text_input("Paper Title:",
                      placeholder="e.g., Attention Is All You Need",
                      key="title_input")

abstract = st.text_area("Abstract:",
                        placeholder="Paste the abstract here...",
                        height=200,
                        key="abstract_input")

if st.button("Classify Paper", type="primary"):
    if not title.strip():
        st.warning("Please enter a title.")
    else:
        with st.spinner('Model is thinking'):
            try:
                text_to_classify = f"{title}. {abstract}".strip()
                inputs = tokenizer(
                    text_to_classify, return_tensors="pt", truncation=True, max_length=512)

                with torch.no_grad():
                    logits = model(**inputs).logits

                probs = torch.sigmoid(logits)[0].numpy()
                predicted_indices = (probs > THRESHOLD).nonzero()[0]

                if len(predicted_indices) == 0:
                    predicted_indices = [probs.argmax()]

                predicted_indices = sorted(
                    predicted_indices, key=lambda idx: probs[idx], reverse=True)

                st.subheader("Analysis Results")

                for idx in predicted_indices:
                    prob = probs[idx]
                    tag = idx2tag[idx]
                    name = tag2name.get(tag, tag)
                    desc = tag2desc.get(tag, "No description available.")

                    color = "#28a745" if prob > 0.7 else "#ffa500" if prob > 0.4 else "#6c757d"

                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### {name} (`{tag}`)")
                            st.write(desc)
                        with col2:
                            colored_progress_bar(float(prob), color)
                            st.write(f"**{prob:.1%} match**")

            except Exception as e:
                st.error(f"Processing error: {e}")
