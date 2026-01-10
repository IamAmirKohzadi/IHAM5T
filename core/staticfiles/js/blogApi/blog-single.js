function formatDateTime(value) {
		if (!value) {
			return "";
		}
		var date = new Date(value);
		if (isNaN(date.getTime())) {
			return "";
		}
		return new Intl.DateTimeFormat("en-GB", {
			day: "2-digit",
			month: "short",
			year: "numeric",
			hour: "2-digit",
			minute: "2-digit"
		}).format(date);
	}

	function getCookie(name) {
		var value = "; " + document.cookie;
		var parts = value.split("; " + name + "=");
		if (parts.length === 2) {
			return parts.pop().split(";").shift();
		}
		return "";
	}

function buildCategories(categoriesInfo, baseUrl) {
	if (!categoriesInfo.length) {
		return '<li><a href="#">Uncategorized</a></li>';
	}
	return categoriesInfo.map(function (cat) {
		var name = cat.name || "";
		var link = baseUrl;
		if (cat.id) {
			link += "?categories=" + encodeURIComponent(cat.id);
		} else {
			link = "#";
		}
			return '<li><a href="' + link + '">' + name + '</a></li>';
		}).join("");
	}

	function renderComments(items, canComment) {
		var byId = {};
		var roots = [];

		items.forEach(function (item) {
			item.children = [];
			byId[item.id] = item;
		});

		items.forEach(function (item) {
			if (item.parent && byId[item.parent]) {
				byId[item.parent].children.push(item);
			} else {
				roots.push(item);
			}
		});

		function renderNode(node) {
			var author = node.author_name || "Anonymous";
			var date = formatDateTime(node.created_date);
			var replyLink = "";
			var reportLink = "";
			var ownerLinks = "";
			var toggleLink = "";
			if (canComment && node.depth < 2) {
				replyLink = '<a href="#" class="comment-reply">Reply</a>';
			}
			if (canComment && !node.is_owner) {
				reportLink = '<a href="#" class="comment-report">Report</a>';
			}
			if (node.is_owner) {
				ownerLinks = '<a href="#" class="comment-edit">Edit</a><a href="#" class="comment-delete">Delete</a>';
			}
			if (node.children.length) {
				toggleLink = '<a href="#" class="comment-toggle" data-count="' + node.children.length + '">Show replies (' +
					node.children.length + ')</a>';
			}
			var html = '<div class="comment-item" data-id="' + node.id + '">' +
				'<div class="comment-meta"><strong>' + author + '</strong> - ' + date + '</div>' +
				'<div class="comment-body">' + (node.message || "") + '</div>' +
				'<div class="comment-actions">' +
					toggleLink +
					replyLink +
					reportLink +
					ownerLinks +
				'</div>';

			if (node.children.length) {
				html += '<div class="comment-children is-collapsed">';
				node.children.forEach(function (child) {
					html += renderNode(child);
				});
				html += '</div>';
			}
			html += '</div>';
			return html;
		}

		var output = "";
		roots.forEach(function (node) {
			output += renderNode(node);
		});
		return output;
	}

	function setSocialLink(selector, url) {
		var $link = $(selector);
		if (url) {
			$link.attr("href", url);
			$link.attr("target", "_blank");
			$link.attr("rel", "noopener");
			$link.attr("title", "");
			$link.removeClass("social-disabled");
			$link.attr("aria-disabled", "false");
		} else {
			$link.removeAttr("href");
			$link.removeAttr("target");
			$link.removeAttr("rel");
			$link.attr("title", "No link available");
			$link.addClass("social-disabled");
			$link.attr("aria-disabled", "true");
		}
	}

	window.addEventListener('load', function () {
		if (!window.jQuery) {
			return;
		}
		var config = document.getElementById("blog-single-config");
		if (!config) {
			return;
		}

		var pathParts = window.location.pathname.split("/").filter(Boolean);
		var postId = pathParts[pathParts.length - 1];
		if (!postId) {
			return;
		}

		var defaultImage = config.dataset.defaultImage;
		var defaultGalleryImage = config.dataset.defaultGalleryImage;
		var apiUrl = config.dataset.postListUrl + postId + "/";

		var commentsUrl = config.dataset.commentsUrl;
		var commentReportUrl = config.dataset.commentReportUrl;
		var postReportUrl = config.dataset.postReportUrl;
		var categoryUrl = config.dataset.categoryUrl;
		var profileUrl = config.dataset.profileUrl;
		var friendRequestsUrl = config.dataset.friendRequestsUrl;
		var friendshipsUrl = config.dataset.friendshipsUrl;
		var blogHomeUrl = config.dataset.blogHomeUrl;
		var loginUrl = config.dataset.loginUrl;
		var csrfToken = getCookie("csrftoken");
		var metaEl = document.getElementById("post-meta");
		var canComment = metaEl && metaEl.dataset.canComment === "true";
		var canReact = metaEl && metaEl.dataset.canReact === "true";
		var isAuthenticated = metaEl && metaEl.dataset.authenticated === "true";
		var categoriesCache = [];
		var currentPost = null;
		var currentProfileId = null;

		function updateCommentCount(total) {
			var safeTotal = parseInt(total, 10);
			if (isNaN(safeTotal)) {
				safeTotal = 0;
			}
			var label = safeTotal + (safeTotal === 1 ? " comment" : " comments");
			$("#post-comments").text(label);
			$("#post-comments-inline").text(label);
		}

		function getResults(data) {
			if (data && Array.isArray(data.results)) {
				return data.results;
			}
			if (Array.isArray(data)) {
				return data;
			}
			return [];
		}

		function setFriendRequestState(state, message) {
			var $wrap = $("#friend-request-wrap");
			var $btn = $("#friend-request-button");
			var $status = $("#friend-request-status");
			if (!state) {
				$wrap.hide();
				return;
			}
			$wrap.show();
			$status.text(message || "");
			if (state === "friends") {
				$btn.text("Friends");
				$btn.prop("disabled", true);
				return;
			}
			if (state === "pending") {
				$btn.text("Request sent");
				$btn.prop("disabled", true);
				return;
			}
			if (state === "incoming") {
				$btn.text("Request received");
				$btn.prop("disabled", true);
				return;
			}
			if (state === "loading") {
				$btn.text("Checking...");
				$btn.prop("disabled", true);
				return;
			}
			$btn.text("Add friend");
			$btn.prop("disabled", false);
		}

		function loadCurrentProfile(callback) {
			$.getJSON(profileUrl, function (data) {
				callback(data);
			}).fail(function () {
				callback(null);
			});
		}

		function checkFriendshipStatus(authorId) {
			$.getJSON(friendshipsUrl, function (data) {
				var items = getResults(data);
				var isFriend = items.some(function (item) {
					return item.friend_id === authorId;
				});
				if (isFriend) {
					setFriendRequestState("friends", "You are friends");
					return;
				}
				$.getJSON(friendRequestsUrl, {
					status: "pending",
					from_profile: currentProfileId,
					to_profile: authorId
				}, function (pendingData) {
					var pendingItems = getResults(pendingData);
					if (pendingItems.length) {
						setFriendRequestState("pending", "Pending response");
						return;
					}
					$.getJSON(friendRequestsUrl, {
						status: "pending",
						from_profile: authorId,
						to_profile: currentProfileId
					}, function (incomingData) {
						var incomingItems = getResults(incomingData);
						if (incomingItems.length) {
							setFriendRequestState("incoming", "Request received");
							return;
						}
						setFriendRequestState("ready", "");
					}).fail(function () {
						setFriendRequestState("ready", "");
					});
				}).fail(function () {
					setFriendRequestState("ready", "");
				});
			}).fail(function () {
				setFriendRequestState("ready", "");
			});
		}

		function initFriendRequest(authorId, isOwner) {
			if (!isAuthenticated || !authorId || isOwner) {
				setFriendRequestState(null, "");
				return;
			}
			loadCurrentProfile(function (data) {
				if (!data || !data.id) {
					setFriendRequestState(null, "");
					return;
				}
				currentProfileId = data.id;
				if (currentProfileId === authorId) {
					setFriendRequestState(null, "");
					return;
				}
				setFriendRequestState("loading", "Checking...");
				checkFriendshipStatus(authorId);
			});
		}

		function sendFriendRequest(authorId) {
			if (!authorId) {
				return;
			}
			$("#friend-request-status").text("Sending...");
			$.ajax({
				url: friendRequestsUrl,
				method: "POST",
				headers: { "X-CSRFToken": csrfToken },
				data: { to_profile: authorId },
				success: function () {
					setFriendRequestState("pending", "Pending response");
				},
				error: function (xhr) {
					var message = "Failed to send request.";
					if (xhr.responseJSON && xhr.responseJSON.detail) {
						message = xhr.responseJSON.detail;
					}
					setFriendRequestState("ready", message);
				}
			});
		}

		function loadCategories(callback) {
			if (categoriesCache.length) {
				callback();
				return;
			}
			$.getJSON(categoryUrl, function (data) {
				var items = data.results || data;
				if (!Array.isArray(items)) {
					items = [];
				}
				categoriesCache = items;
				callback();
			}).fail(function () {
				categoriesCache = [];
				callback();
			});
		}

		function renderCategoryCheckboxes(containerId, selected) {
			var $container = $("#" + containerId);
			$container.empty();
			if (!categoriesCache.length) {
				$container.text("No categories available.");
				return;
			}
			categoriesCache.forEach(function (cat) {
				var name = cat.name || "";
				if (!name) {
					return;
				}
				var checked = selected && selected.indexOf(name) !== -1 ? "checked" : "";
				$container.append(
					'<label><input type="checkbox" value="' + name + '" ' + checked + '> ' + name + '</label>'
				);
			});
		}

		function showEditMessage(text, isSuccess) {
			var $msg = $("#edit-post-message");
			if (!text) {
				$msg.hide();
				$msg.text("");
				$msg.removeClass("success");
				return;
			}
			$msg.text(text);
			$msg.toggleClass("success", Boolean(isSuccess));
			$msg.show();
		}

		function showCommentFormMessage(text) {
			var $msg = $("#comment-form-message");
			if (!text) {
				$msg.hide();
				$msg.text("");
				return;
			}
			$msg.text(text);
			$msg.show();
		}

		function loadComments() {
			$.getJSON(commentsUrl, { post: postId, ordering: "created_date" }, function (data) {
				var comments = data && data.results ? data.results : data;
				if (!Array.isArray(comments)) {
					comments = [];
				}
				var seenIds = {};
				comments = comments.filter(function (item) {
					if (!item || item.id === undefined || item.id === null) {
						return false;
					}
					if (seenIds[item.id]) {
						return false;
					}
					seenIds[item.id] = true;
					return true;
				});
				var total = comments.length;
				if (data && data.total_objects !== undefined) {
					total = data.total_objects;
				} else if (data && data.count !== undefined) {
					total = data.count;
				}
				updateCommentCount(total);

				if (comments.length) {
					$("#comments-list").html(renderComments(comments, canComment));
					$("#comments-empty").hide();
				} else {
					$("#comments-list").empty();
					$("#comments-empty").show();
				}
			}).fail(function () {
				updateCommentCount(0);
				$("#comments-list").empty();
				$("#comments-empty").show();
			});
		}

	$.getJSON(apiUrl, function (data) {
		currentPost = data;
		$("#post-title").text(data.title || "");
		$("#post-title-breadcrumb").text(data.title || "");
		$("#post-title-body").text(data.title || "");
		$("#post-content").html(data.content || "");
		$("#post-date").text(formatDateTime(data.created_date));
		$("#post-views").text(data.counted_view || 0);
		$("#post-like-count").text(data.likes_count || 0);
		$("#post-dislike-count").text(data.dislikes_count || 0);
		$(".post-reaction").removeClass("active");
		if (data.user_reaction === 1) {
			$(".post-like").addClass("active");
		} else if (data.user_reaction === -1) {
			$(".post-dislike").addClass("active");
		}

		var imageUrl = data.image ? data.image : defaultImage;
		$("#post-image").attr("src", imageUrl);
		var image2Url = data.image_2 ? data.image_2 : defaultGalleryImage;
		var image3Url = data.image_3 ? data.image_3 : defaultGalleryImage;
		$("#post-image-2").attr("src", image2Url);
		$("#post-image-3").attr("src", image3Url);
		$("#post-extra-content").text(data.extra_content || "");

		var authorLink = blogHomeUrl;
		if (data.author_id) {
			authorLink += "?author=" + encodeURIComponent(data.author_id);
		}
		$("#post-author").attr("href", authorLink);
		$("#post-author").text(data.author_name || "");
		initFriendRequest(data.author_id, data.can_edit);

		var baseDetail = blogHomeUrl;
		var $prevWrap = $("#post-prev-link").closest(".nav-left");
		var $nextWrap = $("#post-next-link").closest(".nav-right");
		$prevWrap.addClass("nav-hidden");
		$nextWrap.addClass("nav-hidden");
		if (data.previous_post && data.previous_post.id) {
			var prevHref = baseDetail + data.previous_post.id + "/";
			$("#post-prev-link").attr("href", prevHref).text("Previous");
			$("#post-prev-thumb").attr("href", prevHref);
			$("#post-prev-arrow").attr("href", prevHref);
			$prevWrap.removeClass("nav-hidden");
		}

		if (data.next_post && data.next_post.id) {
			var nextHref = baseDetail + data.next_post.id + "/";
			$("#post-next-link").attr("href", nextHref).text("Next");
			$("#post-next-thumb").attr("href", nextHref);
			$("#post-next-arrow").attr("href", nextHref);
			$nextWrap.removeClass("nav-hidden");
		}

		var socialLinks = data.author_social_links || {};
		setSocialLink("#post-author-facebook", socialLinks.facebook);
		setSocialLink("#post-author-twitter", socialLinks.twitter);
		setSocialLink("#post-author-github", socialLinks.github);
		setSocialLink("#post-author-behance", socialLinks.behance);

		var categoriesInfo = Array.isArray(data.categories_info) ? data.categories_info : [];
		if (!categoriesInfo.length && Array.isArray(data.categories)) {
			categoriesInfo = data.categories.map(function (name) {
				return { name: name };
			});
		}
		$("#post-categories").html(buildCategories(categoriesInfo, blogHomeUrl));

		if (data.can_edit) {
			$("#post-actions").show();
			$("#post-report-wrap").hide();
		}
	}).fail(function () {
		window.location.href = blogHomeUrl;
	});

	loadComments();

		function showCommentError($comment, message) {
			var $error = $comment.find(".comment-edit-error");
			if (!$error.length) {
				$error = $('<span class="comment-edit-error"></span>');
				$comment.find(".comment-actions").append($error);
			}
			$error.text(message);
		}

		function clearCommentError($comment) {
			$comment.find(".comment-edit-error").remove();
		}

		$("#comments-list").on("click", ".comment-reply", function (event) {
			event.preventDefault();
			var commentId = $(this).closest(".comment-item").data("id");
			$("#comment-parent-id").val(commentId);
			$("#comment-cancel-reply").show();
			$("#comment-message").focus();
		});

		$("#comments-list").on("click", ".comment-toggle", function (event) {
			event.preventDefault();
			var $toggle = $(this);
			var $comment = $toggle.closest(".comment-item");
			var $children = $comment.children(".comment-children");
			if (!$children.length) {
				return;
			}
			var count = $toggle.data("count") || $children.children(".comment-item").length;
			if ($children.hasClass("is-collapsed")) {
				$children.removeClass("is-collapsed");
				$toggle.text("Hide replies (" + count + ")");
			} else {
				$children.addClass("is-collapsed");
				$toggle.text("Show replies (" + count + ")");
			}
		});

		var reportModal = document.getElementById("report-modal");
		var reportTitle = document.getElementById("report-title");
		var reportReason = document.getElementById("report-reason");
		var reportSubmit = document.getElementById("report-submit");
		var reportCancel = document.getElementById("report-cancel");
		var reportMessage = document.getElementById("report-message");
		var reportTarget = { type: null, id: null };

		function openReportModal(type, targetId) {
			reportTarget.type = type;
			reportTarget.id = targetId;
			reportReason.value = "";
			reportMessage.textContent = "";
			reportMessage.style.display = "none";
			reportMessage.classList.remove("success");
			reportTitle.textContent = type === "post" ? "Report Post" : "Report Comment";
			reportModal.classList.add("is-open");
		}

		function closeReportModal() {
			reportModal.classList.remove("is-open");
			reportTarget.type = null;
			reportTarget.id = null;
		}

		reportCancel.addEventListener("click", function () {
			closeReportModal();
		});

		reportSubmit.addEventListener("click", function () {
			var reason = reportReason.value.trim();
			if (!reason) {
				reportMessage.textContent = "Please enter a reason.";
				reportMessage.style.display = "block";
				return;
			}
			if (!reportTarget.id) {
				reportMessage.textContent = "Nothing selected to report.";
				reportMessage.style.display = "block";
				return;
			}
			var isPost = reportTarget.type === "post";
			var targetUrl = isPost ? postReportUrl : commentReportUrl;
			var payload = isPost ? { post: reportTarget.id, reason: reason } : { comment: reportTarget.id, reason: reason };
			$.ajax({
				url: targetUrl,
				method: "POST",
				headers: { "X-CSRFToken": csrfToken },
				data: payload,
				success: function () {
					reportMessage.textContent = "Report submitted. Thanks.";
					reportMessage.classList.add("success");
					reportMessage.style.display = "block";
					setTimeout(closeReportModal, 800);
				},
				error: function () {
					reportMessage.textContent = isPost ? "Failed to report post." : "Failed to report comment.";
					reportMessage.style.display = "block";
				}
			});
		});

		$("#comments-list").on("click", ".comment-report", function (event) {
			event.preventDefault();
			if (!canComment) {
				window.location.href = loginUrl;
				return;
			}
			var commentId = $(this).closest(".comment-item").data("id");
			openReportModal("comment", commentId);
		});

		$("#post-report-link").on("click", function (event) {
			event.preventDefault();
			if (!canComment) {
				window.location.href = loginUrl;
				return;
			}
			openReportModal("post", postId);
		});

		$("#friend-request-button").on("click", function () {
			if (!isAuthenticated) {
				window.location.href = loginUrl;
				return;
			}
			if (!currentPost || !currentPost.author_id) {
				return;
			}
			sendFriendRequest(currentPost.author_id);
		});

		function showReactionMessage(text) {
			var $msg = $("#post-reaction-message");
			if (!text) {
				$msg.hide();
				$msg.text("");
				return;
			}
			$msg.text(text);
			$msg.show();
		}

		$(".post-reactions").on("click", ".post-reaction", function (event) {
			event.preventDefault();
			showReactionMessage("");
			if (!isAuthenticated) {
				showReactionMessage("Login to react.");
				return;
			}
			if (!canReact) {
				showReactionMessage("Verify your email to react.");
				return;
			}
			var value = $(this).data("value");
			$.ajax({
				url: apiUrl + "react/",
				method: "POST",
				headers: { "X-CSRFToken": csrfToken },
				data: { value: value },
				success: function (response) {
					$("#post-like-count").text(response.likes_count || 0);
					$("#post-dislike-count").text(response.dislikes_count || 0);
					$(".post-reaction").removeClass("active");
					if (response.user_reaction === 1) {
						$(".post-like").addClass("active");
					} else if (response.user_reaction === -1) {
						$(".post-dislike").addClass("active");
					}
				},
				error: function (xhr) {
					var message = "Failed to react.";
					if (xhr.status === 403) {
						message = "Verify your email to react.";
					}
					if (xhr.responseJSON && xhr.responseJSON.detail) {
						message = xhr.responseJSON.detail;
					}
					showReactionMessage(message);
				}
			});
		});

		$("#post-edit-btn").on("click", function () {
			if (!currentPost) {
				return;
			}
			showEditMessage("");
			var categoriesSelected = (currentPost.categories || []).slice();
			$("#post-edit-form")[0].title.value = currentPost.title || "";
			$("#post-edit-form")[0].content.value = currentPost.content || "";
			$("#post-edit-form")[0].extra_content.value = currentPost.extra_content || "";
			if ($("#post-edit-form")[0].status) {
				$("#post-edit-form")[0].status.checked = Boolean(currentPost.status);
			}
			loadCategories(function () {
				renderCategoryCheckboxes("edit-post-categories", categoriesSelected);
				$("#post-edit-modal").addClass("is-open");
			});
		});

		$("#post-edit-cancel").on("click", function () {
			$("#post-edit-modal").removeClass("is-open");
		});

		$("#post-edit-form").on("submit", function (event) {
			event.preventDefault();
			if (!currentPost) {
				return;
			}
			showEditMessage("");
			var form = this;
			var title = form.title.value.trim();
			var content = form.content.value.trim();
			if (!title || !content) {
				showEditMessage("Title and content are required.");
				return;
			}
			var selected = [];
			$("#edit-post-categories input[type='checkbox']:checked").each(function () {
				selected.push($(this).val());
			});
			if (!selected.length) {
				showEditMessage("Select at least one category.");
				return;
			}
			var formData = new FormData();
			formData.append("title", title);
			formData.append("content", content);
			formData.append("extra_content", form.extra_content.value.trim());
			if (form.status) {
				formData.append("status", form.status.checked ? "true" : "false");
			}
			selected.forEach(function (name) {
				formData.append("categories", name);
			});
			if (form.image.files[0]) {
				formData.append("image", form.image.files[0]);
			}
			if (form.image_2.files[0]) {
				formData.append("image_2", form.image_2.files[0]);
			}
			if (form.image_3.files[0]) {
				formData.append("image_3", form.image_3.files[0]);
			}
			$.ajax({
				url: apiUrl,
				method: "PATCH",
				headers: { "X-CSRFToken": csrfToken },
				data: formData,
				processData: false,
				contentType: false,
				success: function () {
					showEditMessage("Post updated.", true);
					setTimeout(function () {
						window.location.reload();
					}, 600);
				},
				error: function (xhr) {
					var message = "Failed to update post.";
					if (xhr.status === 403) {
						message = "Verify your account before editing posts.";
					}
					if (xhr.responseJSON) {
						if (xhr.responseJSON.detail) {
							message = xhr.responseJSON.detail;
						} else {
							var parts = [];
							Object.keys(xhr.responseJSON).forEach(function (key) {
								var value = xhr.responseJSON[key];
								if (Array.isArray(value)) {
									parts.push(key + ": " + value.join(", "));
								} else if (value) {
									parts.push(key + ": " + value);
								}
							});
							if (parts.length) {
								message = parts.join(" | ");
							}
						}
					}
					showEditMessage(message);
				}
			});
		});

		$("#post-delete-btn").on("click", function () {
			if (!currentPost) {
				return;
			}
			$("#post-delete-modal").addClass("is-open");
		});

		$("#post-delete-cancel").on("click", function () {
			$("#post-delete-modal").removeClass("is-open");
		});

		$("#post-delete-confirm").on("click", function () {
			$.ajax({
				url: apiUrl,
				method: "DELETE",
				headers: { "X-CSRFToken": csrfToken },
				success: function () {
					window.location.href = blogHomeUrl;
				},
				error: function () {
					showEditMessage("Failed to delete post.");
				}
			});
		});

		$("#comments-list").on("click", ".comment-edit", function (event) {
			event.preventDefault();
			var $comment = $(this).closest(".comment-item");
			if ($comment.data("editing")) {
				return;
			}
			clearCommentError($comment);
			var currentText = $comment.find(".comment-body").text();
			$comment.data("editing", true);
			$comment.data("original", currentText);

			var $textarea = $('<textarea class="comment-edit-text"></textarea>');
			$textarea.val(currentText);
			$comment.find(".comment-body").empty().append($textarea);

			var $actions = $comment.find(".comment-actions");
			$actions.find(".comment-reply, .comment-report, .comment-toggle, .comment-edit, .comment-delete").hide();
			$actions.append('<a href="#" class="comment-save">Save</a><a href="#" class="comment-cancel">Cancel</a>');
		});

		$("#comments-list").on("click", ".comment-cancel", function (event) {
			event.preventDefault();
			var $comment = $(this).closest(".comment-item");
			var original = $comment.data("original") || "";
			$comment.find(".comment-body").text(original);
			$comment.data("editing", false);
			$comment.find(".comment-save, .comment-cancel").remove();
			$comment.find(".comment-reply, .comment-report, .comment-toggle, .comment-edit, .comment-delete").show();
			clearCommentError($comment);
		});

		$("#comments-list").on("click", ".comment-save", function (event) {
			event.preventDefault();
			var $comment = $(this).closest(".comment-item");
			var commentId = $comment.data("id");
			var message = $comment.find(".comment-edit-text").val().trim();
			if (!message) {
				showCommentError($comment, "Comment cannot be empty.");
				return;
			}
			$.ajax({
				url: commentsUrl + commentId + "/",
				method: "PATCH",
				headers: { "X-CSRFToken": csrfToken },
				data: { message: message },
				success: function () {
					loadComments();
				},
				error: function () {
					showCommentError($comment, "Failed to update comment.");
				}
			});
		});

		$("#comments-list").on("click", ".comment-delete", function (event) {
			event.preventDefault();
			var $comment = $(this).closest(".comment-item");
			var commentId = $comment.data("id");
			if (!window.confirm("Delete this comment and its replies?")) {
				return;
			}
			$.ajax({
				url: commentsUrl + commentId + "/",
				method: "DELETE",
				headers: { "X-CSRFToken": csrfToken },
				success: function () {
					loadComments();
				},
				error: function () {
					showCommentError($comment, "Failed to delete comment.");
				}
			});
		});

		$("#comment-cancel-reply").on("click", function (event) {
			event.preventDefault();
			$("#comment-parent-id").val("");
			$("#comment-cancel-reply").hide();
		});

		$("#comment-form").on("submit", function (event) {
			event.preventDefault();
			showCommentFormMessage("");
			var message = $("#comment-message").val().trim();
			if (!message) {
				showCommentFormMessage("Comment cannot be empty.");
				return;
			}
			var parentId = $("#comment-parent-id").val();
			var payload = { post: postId, message: message };
			if (parentId) {
				payload.parent = parentId;
			}
			$.ajax({
				url: commentsUrl,
				method: "POST",
				headers: { "X-CSRFToken": csrfToken },
				data: payload,
				success: function () {
					$("#comment-message").val("");
					$("#comment-parent-id").val("");
					$("#comment-cancel-reply").hide();
					showCommentFormMessage("");
					loadComments();
				},
				error: function (xhr) {
					var messageText = "Failed to post comment.";
					var responseData = xhr.responseJSON;
					if (!responseData && xhr.responseText) {
						try {
							responseData = JSON.parse(xhr.responseText);
						} catch (e) {
							responseData = null;
						}
					}
					if (xhr.status === 403) {
						messageText = "Verify your account before commenting.";
					}
					if (responseData) {
						if (responseData.detail) {
							messageText = responseData.detail;
						} else if (responseData.non_field_errors) {
							messageText = responseData.non_field_errors.join(" ");
						} else {
							var errorKeys = Object.keys(responseData);
							if (errorKeys.length) {
								var firstValue = responseData[errorKeys[0]];
								if (Array.isArray(firstValue)) {
									messageText = firstValue[0];
								} else if (typeof firstValue === "string") {
									messageText = firstValue;
								}
							}
						}
					}
					showCommentFormMessage(messageText);
				}
			});
		});
	});
