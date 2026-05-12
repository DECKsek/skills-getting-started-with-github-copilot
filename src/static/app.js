document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        const participantsWrapper = document.createElement("div");
        participantsWrapper.className = "participants";

        const participantsTitle = document.createElement("p");
        participantsTitle.innerHTML = "<strong>Participants:</strong>";
        participantsWrapper.appendChild(participantsTitle);

        if (details.participants.length > 0) {
          const participantsList = document.createElement("div");
          participantsList.className = "participants-list";
          details.participants.forEach((participant) => {
            const participantItem = document.createElement("div");
            participantItem.className = "participant-item";
            
            const participantName = document.createElement("span");
            participantName.className = "participant-name";
            participantName.textContent = participant;
            
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.textContent = "🗑️";
            deleteBtn.title = "Remove participant";
            deleteBtn.addEventListener("click", async (e) => {
              e.preventDefault();
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(participant)}`,
                  { method: "POST" }
                );
                if (response.ok) {
                  fetchActivities();
                } else {
                  const error = await response.json();
                  alert(error.detail || "Failed to remove participant");
                }
              } catch (error) {
                alert("Failed to remove participant");
                console.error("Error removing participant:", error);
              }
            });
            
            participantItem.appendChild(participantName);
            participantItem.appendChild(deleteBtn);
            participantsList.appendChild(participantItem);
          });
          participantsWrapper.appendChild(participantsList);
        } else {
          const noParticipants = document.createElement("p");
          noParticipants.className = "info";
          noParticipants.textContent = "No participants yet. Be the first to sign up!";
          participantsWrapper.appendChild(noParticipants);
        }

        activityCard.appendChild(participantsWrapper);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
