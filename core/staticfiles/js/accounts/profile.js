window.addEventListener("load", function () {
		if (!window.fetch) {
			return;
		}
		var config = document.getElementById("profile-config");
		if (!config) {
			return;
		}
		var apiUrl = config.dataset.apiUrl;
		var defaultImage = config.dataset.defaultImage;
		var postsUrlBase = config.dataset.postsUrlBase;
		var postDetailTemplate = config.dataset.postDetailTemplate;
		var postDeleteTemplate = config.dataset.postDeleteTemplate;
		var changePasswordUrl = config.dataset.changePasswordUrl;
		var resendActivationUrl = config.dataset.resendActivationUrl;
		var commentReportUrl = config.dataset.commentReportUrl;
		var postReportUrl = config.dataset.postReportUrl;
		var friendsUrl = config.dataset.friendsUrl;
		var friendRemoveTemplate = config.dataset.friendRemoveTemplate;
		var friendRequestsUrl = config.dataset.friendRequestsUrl;
		var friendRequestAcceptTemplate = config.dataset.friendRequestAcceptTemplate;
		var friendRequestDeclineTemplate = config.dataset.friendRequestDeclineTemplate;
		var postsCache = [];
		var reportsCache = [];
		var friendsCache = [];
		var friendRequestsCache = [];
		var profileData = null;
		var pendingDeleteId = null;

		function formatDateTime(value) {
			if (!value) {
				return "";
			}
			var parsed = new Date(value);
			if (Number.isNaN(parsed.getTime())) {
				return "";
			}
			return parsed.toLocaleString();
		}

		function applyProfileData(data) {
			var firstName = data.first_name || "";
			var lastName = data.last_name || "";
			var fullName = (firstName + " " + lastName).trim();
			document.getElementById("profile-name").textContent = fullName || "Profile";
			document.getElementById("profile-email").textContent = data.email || "";
			document.getElementById("profile-description").textContent = data.description || "No bio yet.";
			document.getElementById("profile-image").src = data.image || defaultImage;
			document.getElementById("profile-created").textContent = formatDateTime(data.created_date) || "-";
			document.getElementById("profile-updated").textContent = formatDateTime(data.updated_date) || "-";

			var facebook = document.getElementById("profile-facebook");
			var twitter = document.getElementById("profile-twitter");
			var github = document.getElementById("profile-github");
			var behance = document.getElementById("profile-behance");

			if (data.facebook_url) {
				facebook.href = data.facebook_url;
				facebook.classList.remove("is-disabled");
			} else {
				facebook.classList.add("is-disabled");
			}

			if (data.twitter_url) {
				twitter.href = data.twitter_url;
				twitter.classList.remove("is-disabled");
			} else {
				twitter.classList.add("is-disabled");
			}

			if (data.github_url) {
				github.href = data.github_url;
				github.classList.remove("is-disabled");
			} else {
				github.classList.add("is-disabled");
			}

			if (data.behance_url) {
				behance.href = data.behance_url;
				behance.classList.remove("is-disabled");
			} else {
				behance.classList.add("is-disabled");
			}
		}

		function buildDetailUrl(postId) {
			return postDetailTemplate.replace("/0/", "/" + postId + "/");
		}

		function buildDeleteUrl(postId) {
			return postDeleteTemplate.replace("/0/", "/" + postId + "/");
		}

		function buildFriendRemoveUrl(friendshipId) {
			return friendRemoveTemplate.replace("/0/", "/" + friendshipId + "/");
		}

		function buildFriendRequestUrl(template, requestId) {
			return template.replace("/0/", "/" + requestId + "/");
		}

		function getCookie(name) {
			var cookieValue = null;
			if (document.cookie && document.cookie !== "") {
				var cookies = document.cookie.split(";");
				for (var i = 0; i < cookies.length; i += 1) {
					var cookie = cookies[i].trim();
					if (cookie.substring(0, name.length + 1) === (name + "=")) {
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
						break;
					}
				}
			}
			return cookieValue;
		}

		function updateCounts() {
			var totalViews = postsCache.reduce(function (sum, post) {
				return sum + (parseInt(post.counted_view, 10) || 0);
			}, 0);
			document.getElementById("profile-post-count").textContent = postsCache.length;
			document.getElementById("profile-view-count").textContent = totalViews;
		}

		function renderPosts(posts) {
			var list = document.getElementById("profile-posts");
			var empty = document.getElementById("profile-posts-empty");
			var errorBox = document.getElementById("profile-posts-error");
			list.innerHTML = "";
			errorBox.style.display = "none";

			postsCache = posts.slice();
			updateCounts();

			if (!postsCache.length) {
				empty.textContent = "No posts yet.";
				empty.style.display = "block";
				return;
			}

			empty.style.display = "none";

			postsCache.forEach(function (post) {
				var row = document.createElement("div");
				row.className = "profile-post-row";

				var info = document.createElement("div");
				info.className = "profile-post-info";

				var isApproved = Boolean(post.status);
				var title;
				if (isApproved) {
					title = document.createElement("a");
					title.className = "profile-post-title";
					title.href = buildDetailUrl(post.id);
				} else {
					title = document.createElement("span");
					title.className = "profile-post-title is-disabled";
				}
				title.textContent = post.title || "Untitled post";

				var excerpt = document.createElement("div");
				excerpt.className = "profile-post-excerpt";
				excerpt.textContent = post.excerpt || "";

				var meta = document.createElement("div");
				meta.className = "profile-post-meta";
				var created = formatDateTime(post.created_date);
				if (created) {
					meta.appendChild(document.createTextNode("Created " + created));
				}
				var statusBadge = document.createElement("span");
				statusBadge.className = "profile-post-status " + (post.status ? "approved" : "pending");
				statusBadge.textContent = post.status ? "Approved" : "Pending approval";
				meta.appendChild(statusBadge);

				info.appendChild(title);
				if (excerpt.textContent) {
					info.appendChild(excerpt);
				}
				if (meta.childNodes.length) {
					info.appendChild(meta);
				}

				var actions = document.createElement("div");
				actions.className = "profile-post-actions";

				if (isApproved) {
					var openLink = document.createElement("a");
					openLink.className = "profile-post-action";
					openLink.href = buildDetailUrl(post.id);
					openLink.textContent = "Open";
					actions.appendChild(openLink);
				}

				if (post.can_edit) {
					var deleteButton = document.createElement("button");
					deleteButton.type = "button";
					deleteButton.className = "profile-post-action is-danger";
					deleteButton.textContent = "Delete";
					deleteButton.addEventListener("click", function () {
						openDeleteModal(post.id);
					});
					actions.appendChild(deleteButton);
				}

				row.appendChild(info);
				row.appendChild(actions);
				list.appendChild(row);
			});
		}

		function renderPostsError(message) {
			var errorBox = document.getElementById("profile-posts-error");
			var empty = document.getElementById("profile-posts-empty");
			errorBox.textContent = message;
			errorBox.style.display = "block";
			empty.style.display = "none";
		}

		function fetchAllPosts(url, collected, onSuccess, onError) {
			fetch(url, { credentials: "same-origin" })
				.then(function (response) {
					if (!response.ok) {
						throw new Error("Failed to load posts.");
					}
					return response.json();
				})
				.then(function (data) {
					var results = data.results || data;
					var updated = collected.concat(results || []);
					if (data.links && data.links.next) {
						fetchAllPosts(data.links.next, updated, onSuccess, onError);
						return;
					}
					onSuccess(updated);
				})
				.catch(function () {
					onError("Could not load posts.");
				});
		}

		function fetchAllItems(url, collected, onSuccess, onError) {
			fetch(url, { credentials: "same-origin" })
				.then(function (response) {
					if (!response.ok) {
						throw new Error("Failed to load data.");
					}
					return response.json();
				})
				.then(function (data) {
					var results = data.results || data;
					if (!Array.isArray(results)) {
						results = [];
					}
					var updated = collected.concat(results);
					if (data.links && data.links.next) {
						fetchAllItems(data.links.next, updated, onSuccess, onError);
						return;
					}
					onSuccess(updated);
				})
				.catch(function () {
					onError("Could not load report data.");
				});
		}

		function renderReportList(items) {
			var list = document.getElementById("profile-report-list");
			var empty = document.getElementById("profile-report-empty");
			list.innerHTML = "";
			document.getElementById("profile-report-count").textContent = items.length;
			if (!items.length) {
				empty.style.display = "block";
				return;
			}
			empty.style.display = "none";
			items.forEach(function (item) {
				var row = document.createElement("div");
				row.className = "profile-report-item";

				var type = document.createElement("div");
				type.className = "profile-report-type";
				type.textContent = item.type === "comment" ? "Comment report" : "Post report";

				var title = document.createElement("div");
				if (item.post_id) {
					var link = document.createElement("a");
					link.className = "profile-report-link";
					link.href = buildDetailUrl(item.post_id);
					link.textContent = item.post_title || ("Post #" + item.post_id);
					title.appendChild(document.createTextNode("On "));
					title.appendChild(link);
				} else {
					title.textContent = "Post unavailable";
				}

				if (item.type === "comment" && item.comment_message) {
					var comment = document.createElement("div");
					comment.textContent = 'Comment: "' + item.comment_message + '"';
					row.appendChild(type);
					row.appendChild(title);
					row.appendChild(comment);
				} else {
					row.appendChild(type);
					row.appendChild(title);
				}

				if (item.reason) {
					var reason = document.createElement("div");
					reason.className = "profile-report-reason";
					reason.textContent = "Reason: " + item.reason;
					row.appendChild(reason);
				}

				list.appendChild(row);
			});
		}

		function renderReportError(message) {
			var errorBox = document.getElementById("profile-report-error");
			var list = document.getElementById("profile-report-list");
			var empty = document.getElementById("profile-report-empty");
			errorBox.textContent = message;
			errorBox.style.display = "block";
			list.innerHTML = "";
			empty.style.display = "none";
			document.getElementById("profile-report-count").textContent = "0";
		}

		function renderFriendsList(items) {
			var list = document.getElementById("profile-friends-list");
			var empty = document.getElementById("profile-friends-empty");
			list.innerHTML = "";
			document.getElementById("profile-friends-count").textContent = items.length;
			if (!items.length) {
				empty.style.display = "block";
				return;
			}
			empty.style.display = "none";
			items.forEach(function (item) {
				var row = document.createElement("div");
				row.className = "profile-friend-item";

				var info = document.createElement("div");
				info.className = "profile-friend-info";

				var name = document.createElement("div");
				name.className = "profile-friend-name";
				name.textContent = item.friend_name || "Friend";

				var email = document.createElement("div");
				email.className = "profile-friend-email";
				email.textContent = item.friend_email || "";

				info.appendChild(name);
				if (email.textContent) {
					info.appendChild(email);
				}

				var removeBtn = document.createElement("button");
				removeBtn.type = "button";
				removeBtn.className = "profile-friend-remove";
				removeBtn.textContent = "Remove";
				removeBtn.addEventListener("click", function () {
					removeFriend(item.id);
				});

				row.appendChild(info);
				row.appendChild(removeBtn);
				list.appendChild(row);
			});
		}

		function renderFriendsError(message) {
			var errorBox = document.getElementById("profile-friends-error");
			var list = document.getElementById("profile-friends-list");
			var empty = document.getElementById("profile-friends-empty");
			errorBox.textContent = message;
			errorBox.style.display = "block";
			list.innerHTML = "";
			empty.style.display = "none";
			document.getElementById("profile-friends-count").textContent = "0";
		}

		function loadFriends() {
			var errorBox = document.getElementById("profile-friends-error");
			errorBox.style.display = "none";
			fetchAllItems(friendsUrl, [], function (items) {
				friendsCache = items;
				renderFriendsList(friendsCache);
			}, function () {
				renderFriendsError("Could not load friends.");
			});
		}

		function removeFriend(friendshipId) {
			var csrfToken = getCookie("csrftoken");
			var removeUrl = buildFriendRemoveUrl(friendshipId);
			fetch(removeUrl, {
				method: "POST",
				credentials: "same-origin",
				headers: {
					"X-CSRFToken": csrfToken
				}
			})
				.then(function (response) {
					if (!response.ok) {
						throw new Error("Failed to remove friend.");
					}
					friendsCache = friendsCache.filter(function (item) {
						return item.id !== friendshipId;
					});
					renderFriendsList(friendsCache);
				})
				.catch(function () {
					renderFriendsError("Could not remove friend.");
				});
		}

		function renderFriendRequestsList(items) {
			var list = document.getElementById("profile-requests-list");
			var empty = document.getElementById("profile-requests-empty");
			list.innerHTML = "";
			document.getElementById("profile-requests-count").textContent = items.length;
			if (!items.length) {
				empty.style.display = "block";
				return;
			}
			empty.style.display = "none";
			items.forEach(function (item) {
				var row = document.createElement("div");
				row.className = "profile-request-item";

				var info = document.createElement("div");
				info.className = "profile-request-info";

				var name = document.createElement("div");
				name.className = "profile-request-name";
				name.textContent = item.from_name || "User";

				info.appendChild(name);

				var actions = document.createElement("div");
				actions.className = "profile-request-actions";

				var acceptBtn = document.createElement("button");
				acceptBtn.type = "button";
				acceptBtn.className = "profile-request-action accept";
				acceptBtn.textContent = "Accept";
				acceptBtn.addEventListener("click", function () {
					acceptFriendRequest(item.id);
				});

				var declineBtn = document.createElement("button");
				declineBtn.type = "button";
				declineBtn.className = "profile-request-action decline";
				declineBtn.textContent = "Decline";
				declineBtn.addEventListener("click", function () {
					declineFriendRequest(item.id);
				});

				actions.appendChild(acceptBtn);
				actions.appendChild(declineBtn);

				row.appendChild(info);
				row.appendChild(actions);
				list.appendChild(row);
			});
		}

		function renderFriendRequestsError(message) {
			var errorBox = document.getElementById("profile-requests-error");
			var list = document.getElementById("profile-requests-list");
			var empty = document.getElementById("profile-requests-empty");
			errorBox.textContent = message;
			errorBox.style.display = "block";
			list.innerHTML = "";
			empty.style.display = "none";
			document.getElementById("profile-requests-count").textContent = "0";
		}

		function loadFriendRequests(profileId) {
			if (!profileId) {
				return;
			}
			var errorBox = document.getElementById("profile-requests-error");
			errorBox.style.display = "none";
			var requestsUrl = friendRequestsUrl + "?status=pending&to_profile=" + encodeURIComponent(profileId);
			fetchAllItems(requestsUrl, [], function (items) {
				friendRequestsCache = items;
				renderFriendRequestsList(friendRequestsCache);
			}, function () {
				renderFriendRequestsError("Could not load friend requests.");
			});
		}

		function acceptFriendRequest(requestId) {
			var csrfToken = getCookie("csrftoken");
			var acceptUrl = buildFriendRequestUrl(friendRequestAcceptTemplate, requestId);
			fetch(acceptUrl, {
				method: "POST",
				credentials: "same-origin",
				headers: {
					"X-CSRFToken": csrfToken
				}
			})
				.then(function (response) {
					if (!response.ok) {
						throw new Error("Failed to accept request.");
					}
					friendRequestsCache = friendRequestsCache.filter(function (item) {
						return item.id !== requestId;
					});
					renderFriendRequestsList(friendRequestsCache);
					loadFriends();
				})
				.catch(function () {
					renderFriendRequestsError("Could not accept request.");
				});
		}

		function declineFriendRequest(requestId) {
			var csrfToken = getCookie("csrftoken");
			var declineUrl = buildFriendRequestUrl(friendRequestDeclineTemplate, requestId);
			fetch(declineUrl, {
				method: "POST",
				credentials: "same-origin",
				headers: {
					"X-CSRFToken": csrfToken
				}
			})
				.then(function (response) {
					if (!response.ok) {
						throw new Error("Failed to decline request.");
					}
					friendRequestsCache = friendRequestsCache.filter(function (item) {
						return item.id !== requestId;
					});
					renderFriendRequestsList(friendRequestsCache);
				})
				.catch(function () {
					renderFriendRequestsError("Could not decline request.");
				});
		}

		function loadApprovedReports() {
			var errorBox = document.getElementById("profile-report-error");
			errorBox.style.display = "none";
			fetchAllItems(commentReportUrl, [], function (commentReports) {
				fetchAllItems(postReportUrl, [], function (postReports) {
					var merged = [];
					commentReports.forEach(function (item) {
						merged.push({
							type: "comment",
							id: item.id,
							post_id: item.post_id,
							post_title: item.post_title,
							comment_message: item.comment_message,
							reason: item.reason
						});
					});
					postReports.forEach(function (item) {
						merged.push({
							type: "post",
							id: item.id,
							post_id: item.post,
							post_title: item.post_title,
							reason: item.reason
						});
					});
					reportsCache = merged;
					renderReportList(reportsCache);
				}, renderReportError);
			}, renderReportError);
		}

		function loadPosts(profileId) {
			var postsUrl = postsUrlBase + "?author=" + encodeURIComponent(profileId) + "&include_unapproved=1";
			fetchAllPosts(postsUrl, [], renderPosts, renderPostsError);
		}

		function openReportModal() {
			document.getElementById("profile-report-modal").style.display = "flex";
		}

		function closeReportModal() {
			document.getElementById("profile-report-modal").style.display = "none";
		}

		function openFriendsModal() {
			document.getElementById("profile-friends-modal").style.display = "flex";
		}

		function closeFriendsModal() {
			document.getElementById("profile-friends-modal").style.display = "none";
		}

		function openRequestsModal() {
			document.getElementById("profile-requests-modal").style.display = "flex";
		}

		function closeRequestsModal() {
			document.getElementById("profile-requests-modal").style.display = "none";
		}

		function showProfileEditMessage(text, isSuccess) {
			var message = document.getElementById("profile-edit-message");
			if (!text) {
				message.style.display = "none";
				message.textContent = "";
				message.classList.remove("success");
				return;
			}
			message.textContent = text;
			message.classList.toggle("success", Boolean(isSuccess));
			message.style.display = "block";
		}

		function openProfileEditModal() {
			if (!profileData) {
				return;
			}
			showProfileEditMessage("");
			document.getElementById("profile-first-name").value = profileData.first_name || "";
			document.getElementById("profile-last-name").value = profileData.last_name || "";
			document.getElementById("profile-description-input").value = profileData.description || "";
			document.getElementById("profile-facebook-input").value = profileData.facebook_url || "";
			document.getElementById("profile-twitter-input").value = profileData.twitter_url || "";
			document.getElementById("profile-github-input").value = profileData.github_url || "";
			document.getElementById("profile-behance-input").value = profileData.behance_url || "";
			document.getElementById("profile-image-input").value = "";
			document.getElementById("profile-edit-modal").style.display = "flex";
		}

		function closeProfileEditModal() {
			document.getElementById("profile-edit-modal").style.display = "none";
		}

		function showPasswordMessage(text, isSuccess) {
			var message = document.getElementById("profile-password-message");
			if (!text) {
				message.style.display = "none";
				message.textContent = "";
				message.classList.remove("success");
				return;
			}
			message.textContent = text;
			message.classList.toggle("success", Boolean(isSuccess));
			message.style.display = "block";
		}

		function openPasswordModal() {
			showPasswordMessage("");
			document.getElementById("profile-password-form").reset();
			document.getElementById("profile-password-modal").style.display = "flex";
		}

		function closePasswordModal() {
			document.getElementById("profile-password-modal").style.display = "none";
		}

		function showResendMessage(text, isSuccess) {
			var message = document.getElementById("profile-resend-message");
			if (!message) {
				return;
			}
			if (!text) {
				message.style.display = "none";
				message.textContent = "";
				message.classList.remove("success");
				return;
			}
			message.textContent = text;
			message.classList.toggle("success", Boolean(isSuccess));
			message.style.display = "block";
		}

		function openDeleteModal(postId) {
			pendingDeleteId = postId;
			document.getElementById("profile-delete-modal").style.display = "flex";
		}

		function closeDeleteModal() {
			pendingDeleteId = null;
			document.getElementById("profile-delete-modal").style.display = "none";
		}

		function deletePost(postId) {
			var csrfToken = getCookie("csrftoken");
			var deleteUrl = buildDeleteUrl(postId);
			fetch(deleteUrl, {
				method: "DELETE",
				credentials: "same-origin",
				headers: {
					"X-CSRFToken": csrfToken
				}
			})
				.then(function (response) {
					if (!response.ok) {
						throw new Error("Failed to delete post.");
					}
					postsCache = postsCache.filter(function (post) {
						return post.id !== postId;
					});
					renderPosts(postsCache);
					closeDeleteModal();
				})
				.catch(function () {
					renderPostsError("Could not delete the post.");
					closeDeleteModal();
				});
		}

		document.getElementById("profile-delete-cancel").addEventListener("click", closeDeleteModal);
		document.getElementById("profile-delete-confirm").addEventListener("click", function () {
			if (pendingDeleteId) {
				deletePost(pendingDeleteId);
			}
		});
		document.getElementById("profile-report-button").addEventListener("click", openReportModal);
		document.getElementById("profile-report-close").addEventListener("click", closeReportModal);
		document.getElementById("profile-friends-button").addEventListener("click", openFriendsModal);
		document.getElementById("profile-friends-close").addEventListener("click", closeFriendsModal);
		document.getElementById("profile-requests-button").addEventListener("click", openRequestsModal);
		document.getElementById("profile-requests-close").addEventListener("click", closeRequestsModal);
		document.getElementById("profile-edit-button").addEventListener("click", openProfileEditModal);
		document.getElementById("profile-edit-cancel").addEventListener("click", closeProfileEditModal);
		document.getElementById("profile-password-button").addEventListener("click", openPasswordModal);
		document.getElementById("profile-password-cancel").addEventListener("click", closePasswordModal);
		var resendButton = document.getElementById("profile-resend-button");
		if (resendButton) {
			resendButton.addEventListener("click", function () {
				showResendMessage("");
				fetch(resendActivationUrl, {
					method: "POST",
					credentials: "same-origin",
					headers: {
						"Content-Type": "application/json",
						"X-CSRFToken": getCookie("csrftoken")
					},
					body: JSON.stringify({ email: profileData ? profileData.email : "" })
				})
					.then(function (response) {
						return response.json().then(function (data) {
							if (!response.ok) {
								throw data;
							}
							return data;
						});
					})
					.then(function () {
						showResendMessage("Verification email sent.", true);
					})
					.catch(function (data) {
						if (data && data.detail) {
							showResendMessage(data.detail);
							return;
						}
						if (data && data.email) {
							showResendMessage(data.email.join(", "));
							return;
						}
						showResendMessage("Could not resend verification email.");
					});
			});
		}
		document.getElementById("profile-password-form").addEventListener("submit", function (event) {
			event.preventDefault();
			showPasswordMessage("");
			var oldPassword = document.getElementById("password-old").value.trim();
			var newPassword = document.getElementById("password-new").value.trim();
			var newPasswordConfirm = document.getElementById("password-new-confirm").value.trim();
			if (!oldPassword || !newPassword || !newPasswordConfirm) {
				showPasswordMessage("All fields are required.");
				return;
			}
			fetch(changePasswordUrl, {
				method: "PUT",
				credentials: "same-origin",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": getCookie("csrftoken")
				},
				body: JSON.stringify({
					old_password: oldPassword,
					new_password: newPassword,
					new_password1: newPasswordConfirm
				})
			})
				.then(function (response) {
					return response.json().then(function (data) {
						if (!response.ok) {
							throw data;
						}
						return data;
					});
				})
				.then(function () {
					showPasswordMessage("Password updated.", true);
					setTimeout(closePasswordModal, 700);
				})
				.catch(function (data) {
					if (data && data.detail) {
						showPasswordMessage(data.detail);
						return;
					}
					if (data && data.old_password) {
						showPasswordMessage(data.old_password.join(", "));
						return;
					}
					if (data && data.new_password) {
						showPasswordMessage(data.new_password.join(", "));
						return;
					}
					showPasswordMessage("Failed to change password.");
				});
		});
		document.getElementById("profile-edit-form").addEventListener("submit", function (event) {
			event.preventDefault();
			showProfileEditMessage("");
			var formData = new FormData();
			formData.append("first_name", document.getElementById("profile-first-name").value.trim());
			formData.append("last_name", document.getElementById("profile-last-name").value.trim());
			formData.append("description", document.getElementById("profile-description-input").value.trim());
			formData.append("facebook_url", document.getElementById("profile-facebook-input").value.trim());
			formData.append("twitter_url", document.getElementById("profile-twitter-input").value.trim());
			formData.append("github_url", document.getElementById("profile-github-input").value.trim());
			formData.append("behance_url", document.getElementById("profile-behance-input").value.trim());

			var imageInput = document.getElementById("profile-image-input");
			if (imageInput.files[0]) {
				formData.append("image", imageInput.files[0]);
			}

			fetch(apiUrl, {
				method: "PATCH",
				credentials: "same-origin",
				headers: {
					"X-CSRFToken": getCookie("csrftoken")
				},
				body: formData
			})
				.then(function (response) {
					if (!response.ok) {
						throw new Error("Failed to update profile.");
					}
					return response.json();
				})
				.then(function (data) {
					profileData = data;
					applyProfileData(profileData);
					showProfileEditMessage("Profile updated.", true);
					setTimeout(closeProfileEditModal, 700);
				})
				.catch(function () {
					showProfileEditMessage("Could not update profile.");
				});
		});

		fetch(apiUrl, { credentials: "same-origin" })
			.then(function (response) {
				if (!response.ok) {
					throw new Error("Failed to load profile.");
				}
				return response.json();
			})
			.then(function (data) {
				profileData = data;
				applyProfileData(profileData);
				if (data.id) {
					loadPosts(data.id);
				} else {
					renderPostsError("Missing profile id for posts.");
				}
				loadApprovedReports();
				loadFriends();
				loadFriendRequests(data.id);
			})
			.catch(function () {
				var errorBox = document.getElementById("profile-error");
				errorBox.textContent = "Could not load profile data.";
				errorBox.style.display = "block";
				renderPostsError("Could not load posts.");
			});
	});
