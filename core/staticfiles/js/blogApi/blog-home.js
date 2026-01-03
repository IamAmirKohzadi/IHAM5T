function getCookie(name) {
						var value = "; " + document.cookie;
						var parts = value.split("; " + name + "=");
						if (parts.length === 2) {
							return parts.pop().split(";").shift();
						}
						return "";
					}

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

					function buildCategoryItems(categoriesInfo, baseUrl) {
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

					window.addEventListener('load', function () {
						if (!window.jQuery) {
							return;
						}
						var config = document.getElementById("blog-home-config");
						if (!config) {
							return;
						}
						var baseUrl = config.dataset.blogHomeUrl;
						var postListUrl = config.dataset.postListUrl;
						var defaultImage = config.dataset.defaultImage;

						var params = new URLSearchParams(window.location.search);
						var page = parseInt(params.get('page') || '1', 10);
						var apiUrl = postListUrl + "?page=" + page;
						var ordering = params.get('ordering');
						var query = params.get('search');
						if (query) {
							apiUrl += "&search=" + encodeURIComponent(query);
						}
						var category = params.get('categories') || params.get('category');
						if (category) {
							apiUrl += "&categories=" + encodeURIComponent(category);
						}
						if (ordering) {
							apiUrl += "&ordering=" + encodeURIComponent(ordering);
						}

						$("#filter-ordering").val(ordering || "");

						$.getJSON(apiUrl, function (data) {
							var posts = data.results || data;
							var $list = $("#posts-list");
							var $pagination = $("#posts-pagination");
							$list.empty();
							$pagination.empty();

							if (data.number_of_pages && page > data.number_of_pages) {
								window.location.href = baseUrl;
								return;
							}

							posts.forEach(function (p) {
								var $item = $($("#post-template").html());
								var imageUrl = p.image ? p.image : defaultImage;
								var categoriesInfo = Array.isArray(p.categories_info) ? p.categories_info : [];
								if (!categoriesInfo.length && Array.isArray(p.categories)) {
									categoriesInfo = p.categories.map(function (name) {
										return { name: name };
									});
								}
								var categoryLinks = buildCategoryItems(categoriesInfo, baseUrl);
								$item.find(".post-title").text(p.title || "");
								$item.find(".post-link").attr("href", p.id ? (baseUrl + p.id + "/") : "#");
								$item.find(".post-excerpt").text(p.excerpt || "");
								$item.find(".post-image").attr("src", imageUrl);
								var authorLink = baseUrl;
								if (p.author_id) {
									authorLink += "?author=" + encodeURIComponent(p.author_id);
								}
								$item.find(".post-author").attr("href", authorLink);
								$item.find(".post-author").text(p.author_name || "");
								$item.find(".post-categories").html(categoryLinks);
								$item.find(".post-date").text(formatDateTime(p.created_date));
								$item.find(".post-views").text(p.counted_view || 0);
								var commentCount = parseInt(p.comments_count, 10);
								if (isNaN(commentCount)) {
									commentCount = 0;
								}
								var commentLabel = commentCount + (commentCount === 1 ? " comment" : " comments");
								$item.find(".post-comments").text(commentLabel);
								$item.find(".post-like-count").text(p.likes_count || 0);
								$item.find(".post-dislike-count").text(p.dislikes_count || 0);
								if (p.user_reaction === 1) {
									$item.find(".post-like").addClass("active");
								} else if (p.user_reaction === -1) {
									$item.find(".post-dislike").addClass("active");
								}
								if (p.urls && p.urls.relative) {
									$item.data("react-url", p.urls.relative + "react/");
								}
								$list.append($item);
							});

							if (data.number_of_pages) {
								for (var i = 1; i <= data.number_of_pages; i++) {
									var active = (i === page) ? " active" : "";
									var link = "?page=" + i;
									if (query) {
										link += "&search=" + encodeURIComponent(query);
									}
									if (category) {
										link += "&categories=" + encodeURIComponent(category);
									}
									if (ordering) {
										link += "&ordering=" + encodeURIComponent(ordering);
									}
									$pagination.append(
										'<li class="page-item' + active + '"><a class="page-link" href="' + link + '">' + i + '</a></li>'
									);
								}
							}
						}).fail(function () {
							window.location.href = baseUrl;
						});

						var reactMeta = document.getElementById("post-react-meta");
						var isAuthenticated = reactMeta && reactMeta.dataset.authenticated === "true";
						var isVerified = reactMeta && reactMeta.dataset.verified === "true";
						var canReact = isAuthenticated && isVerified;

						function showReactionMessage($item, message) {
							var $msg = $item.find(".post-reaction-message");
							if (!message) {
								$msg.hide();
								$msg.text("");
								return;
							}
							$msg.text(message);
							$msg.show();
						}

						$("#posts-list").on("click", ".post-reaction", function (event) {
							event.preventDefault();
							var $item = $(this).closest(".single-post");
							showReactionMessage($item, "");
							if (!isAuthenticated) {
								showReactionMessage($item, "Login to react.");
								return;
							}
							if (!canReact) {
								showReactionMessage($item, "Verify your email to react.");
								return;
							}
							var reactUrl = $item.data("react-url");
							if (!reactUrl) {
								showReactionMessage($item, "Reaction not available.");
								return;
							}
							var value = $(this).data("value");
							$.ajax({
								url: reactUrl,
								method: "POST",
								headers: { "X-CSRFToken": getCookie("csrftoken") },
								data: { value: value },
								success: function (response) {
									$item.find(".post-like-count").text(response.likes_count || 0);
									$item.find(".post-dislike-count").text(response.dislikes_count || 0);
									$item.find(".post-like, .post-dislike").removeClass("active");
									if (response.user_reaction === 1) {
										$item.find(".post-like").addClass("active");
									} else if (response.user_reaction === -1) {
										$item.find(".post-dislike").addClass("active");
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
									showReactionMessage($item, message);
								}
							});
						});

						var categoriesCache = [];
						var categoryUrl = config.dataset.categoryUrl;
						var postCreateUrl = postListUrl;
						var $createModal = $("#create-post-modal");
						var $createMessage = $("#create-post-message");

						function showCreateMessage(text, isSuccess) {
							if (!text) {
								$createMessage.hide();
								$createMessage.text("");
								$createMessage.removeClass("success");
								return;
							}
							$createMessage.text(text);
							$createMessage.toggleClass("success", Boolean(isSuccess));
							$createMessage.show();
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

						$("#create-post-button").on("click", function () {
							showCreateMessage("");
							loadCategories(function () {
								renderCategoryCheckboxes("create-post-categories", []);
								$createModal.addClass("is-open");
							});
						});

						$("#create-post-cancel").on("click", function () {
							$createModal.removeClass("is-open");
						});

						$("#create-post-form").on("submit", function (event) {
							event.preventDefault();
							showCreateMessage("");
							var form = this;
							var formData = new FormData();
							var title = form.title.value.trim();
							var content = form.content.value.trim();
							if (!title || !content) {
								showCreateMessage("Title and content are required.");
								return;
							}
							formData.append("title", title);
							formData.append("content", content);
							if (form.extra_content.value.trim()) {
								formData.append("extra_content", form.extra_content.value.trim());
							}
							if (form.status) {
								formData.append("status", form.status.checked ? "true" : "false");
							}

							var selected = [];
							$("#create-post-categories input[type='checkbox']:checked").each(function () {
								selected.push($(this).val());
							});
							if (!selected.length) {
								showCreateMessage("Select at least one category.");
								return;
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
								url: postCreateUrl,
								method: "POST",
								headers: { "X-CSRFToken": getCookie("csrftoken") },
								data: formData,
								processData: false,
								contentType: false,
								success: function () {
									showCreateMessage("Post created successfully.", true);
									form.reset();
									setTimeout(function () {
										window.location.reload();
									}, 600);
								},
								error: function (xhr) {
									var message = "Failed to create post.";
									if (xhr.status === 403) {
										message = "Verify your account before creating posts.";
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
									showCreateMessage(message);
								}
							});
						});
					});
