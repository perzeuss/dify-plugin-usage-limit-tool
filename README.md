## Usage Limit Tool

**Author:** perzeuss  
**Version:** 0.1.0  
**Type:** Extension  

---

### Description

The Usage Limit Tool is designed to manage and monitor user interactions within Dify chatflows by applying specified message limits. This tool helps prevent abuse, avoid unwanted costs, and implement user-specific usage plans by defining message limits through various strategies. By utilizing different configurations, the tool allows you to enforce restrictions flexibly and efficiently.

### Getting Started

To use the Usage Limit Tool effectively, you should specify the `user_id` and other parameters like the tracking method, limit, usage limit reset interval, and strategy when setting it up.

### Tracking Methods

The tool offers several tracking methods that dictate how message limits are applied:

1. **Workspace User (workspace-user)**  
   Limits messages for users across all Dify apps within the workspace.  
   *Example Scenario:* You want to limit a user's total message count irrespective of the app they dialog with.

2. **App User (app-user)**  
   Limits messages for users of a specific Dify app.  
   *Example Scenario:* Each app has its distinct purpose or cost, and you want to ensure users don't exceed the limit per app.

3. **Conversation**  
   Limits messages per individual conversation.  
   *Example Scenario:* Encourage users to start a new conversation after hitting a message limit to avoid overly long threads, which can be costly or result in cumbersome analyses/summaries.

4. **App**  
   Limits messages per app for all users collectively.  
   *Example Scenario:* You want to ensure the total user activity within an application does not exceed a maximum number, regardless of the individual user interactions.

### Limit Strategies

Two windowing strategies determine the limit reset behavior:

1. **Fixed Window**  
   Resets the limit after a predefined interval, requiring users to wait until the window closes.  
   *Example Scenario:* Users can send a maximum of 100 messages, and the limit resets precisely every hour regardless of their activity.

2. **Sliding Window**  
   Offers better experience by gradually resetting from the user's first message.  
   *Example Scenario:* Allows users to begin re-sending messages sooner as older messages fall outside the window.

### Usage Limit Reset Interval

Configure how often the usage limits reset:

- **Hour**: Limit messages per hour
- **Day**: Limit messages per day
- **Week**: Limit messages per week
- **Month**: Limit messages per month
- **Year**: Limit messages per year

*Example Scenario:* You may combine different intervals to impose both hourly and daily limits for comprehensive usage control.

### Example Configurations

- **Protecting from Abuse:** Apply conversation message limits to enforce the creation of new talks after 50 messages.
- **Avoiding Unwanted Costs:** Set a daily limit on messages per user to control daily usage costs effectively.
- **Implementing Usage Plans:** Offer users message quotas based on subscription levels by employing app-wide limits.

### Usage Scenarios

The Usage Limit Tool can be deployed multiple times with varied configurations for broader control. For instance, enforce per-hour as well as per-day limits, or combine conversation-based restrictions with user-specific quotas.

### Reset Usage Tool

In addition to tracking limits, a companion tool is available to manually or programmatically reset usage. This is useful for debugging or aligning with custom workflow logic when temporary resets are necessary.

### Additional Information

- **Nature of Limits:** These are not strict system rate limits but specific to managing chat messages sent to a Dify.ai chatflow.
- **Tool Operation:** The Usage Limit Tool tracks usage and limits flow by branching out when limits are exceeded. This facilitates alternate paths in chatflow designs based on whether a user hits their limit.

### Acknowledgments

Special thanks to the Dify team for their outstanding support and resources. This capability-rich tool was developed with their guidance during the Dify 1.0-beta program. ❤️