CLUSTER_DETAILS: dict[int, dict[str, object]] = {
    0: {
        "cluster_name": "Recent Low Buyers",
        "business_summary": "This customer is active recently but still early in value growth.",
        "recommended_actions": [
            "Offer onboarding campaigns",
            "Promote first-purchase incentives",
            "Send engagement nudges",
        ],
    },
    1: {
        "cluster_name": "High Value & Highly Engaged",
        "business_summary": "This customer belongs to the highest-value segment.",
        "recommended_actions": [
            "Offer VIP rewards",
            "Launch referral campaigns",
            "Provide exclusive access",
        ],
    },
    2: {
        "cluster_name": "Stable Repeat Buyers",
        "business_summary": "This customer shows consistent purchasing behavior and retention potential.",
        "recommended_actions": [
            "Promote cross-sell opportunities",
            "Run retention campaigns",
            "Recommend personalized bundles",
        ],
    },
    3: {
        "cluster_name": "At-Risk Low-Value Buyers",
        "business_summary": "This customer may be drifting toward churn and needs reactivation.",
        "recommended_actions": [
            "Run win-back campaigns",
            "Offer churn-prevention discounts",
            "Send reactivation emails",
        ],
    },
}

