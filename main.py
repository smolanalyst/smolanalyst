from dotenv import load_dotenv
from smolagents import CodeAgent, HfApiModel

load_dotenv()


def main():
    print("Hello from smolanalyst!")

    model = HfApiModel()

    agent = CodeAgent(
        model=model,
        tools=[],
        add_base_tools=True,
        additional_authorized_imports=[
            "numpy",
            "pandas",
            "scikit-learn",
            "matplotlib.pyplot",
        ],
    )

    prompt = """
    You are a machine learning specialist. A data file is available at data/dataset.tsv.
    Give me a cumulative chart of the amounts in dollar over time.
    """

    agent.run(prompt)


if __name__ == "__main__":
    main()
