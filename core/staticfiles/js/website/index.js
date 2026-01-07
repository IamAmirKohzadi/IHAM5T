(function () {
	function truncateText(value, maxLength) {
		if (!value) {
			return "";
		}
		if (value.length <= maxLength) {
			return value;
		}
		return value.slice(0, maxLength).trim() + "...";
	}

	function truncateWords(value, maxWords) {
		if (!value) {
			return "";
		}
		var words = value.trim().split(/\s+/);
		if (words.length <= maxWords) {
			return value.trim();
		}
		return words.slice(0, maxWords).join(" ") + "...";
	}

	function formatDate(value) {
		var date = new Date(value);
		if (Number.isNaN(date.getTime())) {
			return "";
		}
		return date.toLocaleDateString("en-US", {
			year: "numeric",
			month: "short",
			day: "numeric"
		});
	}

	function buildTopStoryCard(post, baseUrl, defaultImage) {
		var imageUrl = defaultImage;
		var title = post.title || "Untitled";
		var excerpt = post.excerpt || post.content || "";
		excerpt = truncateWords(excerpt, 10);
		var link = baseUrl;
		if (post.id) {
			link += post.id + "/";
		}

		var $col = $("<div>").addClass("col-lg-4");
		var $card = $("<div>").addClass("single-destination relative");
		var $thumb = $("<div>").addClass("thumb relative");
		var $overlay = $("<div>").addClass("overlay overlay-bg");
		var $img = $("<img>").addClass("img-fluid").attr("src", imageUrl).attr("alt", "");
		var $desc = $("<div>").addClass("desc");
		var $btn = $("<a>").addClass("price-btn").attr("href", link).text("Read");
		var $title = $("<h4>").text(title);
		var views = typeof post.counted_view === "number" ? post.counted_view : 0;
		var $excerpt = $("<p>").text(excerpt);
		var $views = $("<p>").addClass("top-story-views").text("Views: " + views);

		$thumb.append($overlay, $img);
		$desc.append($btn, $title, $excerpt, $views);
		$card.append($thumb, $desc);
		$col.append($card);
		return $col;
	}

	function buildCategoryCard(category, baseUrl, defaultImage) {
		var imageUrl = category.image || defaultImage;
		var name = category.name || "";
		var description = category.description || "";
		var link = baseUrl;
		if (category.id) {
			link += "?categories=" + encodeURIComponent(category.id);
		}

		var $card = $($("#home-category-template").html());
		$card.find(".category-image").attr("src", imageUrl);
		$card.find(".category-link").attr("href", link);
		$card.find(".category-name").text(name);
		$card.find(".category-description").text(description);
		return $card;
	}

	function buildLatestPostCard(post, baseUrl, defaultImage) {
		var templateHtml = $("#latest-post-template").html();
		if (!templateHtml) {
			return null;
		}
		var $card = $(templateHtml);
		var imageUrl = post.image || defaultImage;
		var title = post.title || "Untitled";
		var excerpt = post.excerpt || post.content || "";
		excerpt = truncateWords(excerpt, 15);
		var createdDate = post.created_date ? formatDate(post.created_date) : "";
		var link = baseUrl;
		if (post.id) {
			link += post.id + "/";
		}

		$card.find(".latest-post-image").attr("src", imageUrl);
		$card.find(".latest-post-link").attr("href", link);
		$card.find(".latest-post-title").text(title);
		$card.find(".latest-post-excerpt").text(excerpt);
		$card.find(".latest-post-date").text(createdDate);

		var categories = [];
		if (Array.isArray(post.categories_info)) {
			categories = post.categories_info;
		} else if (Array.isArray(post.categories)) {
			categories = post.categories.map(function (name) {
				return { name: name };
			});
		}

		var $categoryList = $card.find(".latest-post-categories");
		if ($categoryList.length) {
			$categoryList.empty();
			if (!categories.length) {
				$card.find(".latest-post-tags").remove();
			} else {
				categories.forEach(function (category) {
					var name = category.name || "";
					if (!name) {
						return;
					}
					var $item = $("<li>");
					var $link = $("<a>").attr("href", baseUrl);
					if (category.id) {
						$link.attr("href", baseUrl + "?categories=" + encodeURIComponent(category.id));
					}
					$link.text(name);
					$item.append($link);
					$categoryList.append($item);
				});
			}
		}

		return $card;
	}

	function initLatestCarousel($carousel, itemCount) {
		if (!$carousel.length || !$.fn.owlCarousel) {
			return;
		}
		if ($carousel.hasClass("owl-loaded")) {
			$carousel.trigger("destroy.owl.carousel");
			$carousel.removeClass("owl-loaded owl-hidden");
			$carousel.find(".owl-stage-outer").children().unwrap();
			$carousel.find(".owl-item").children().unwrap();
		}
		var loopEnabled = itemCount > 3;
		var dotsEnabled = itemCount > 1;
		var autoplayEnabled = itemCount > 1;
		$carousel.owlCarousel({
			items: 3,
			loop: loopEnabled,
			margin: 30,
			dots: dotsEnabled,
			autoplayHoverPause: true,
			smartSpeed: 500,
			autoplay: autoplayEnabled,
			responsive: {
				0: {
					items: 1
				},
				480: {
					items: 1
				},
				768: {
					items: 2
				},
				961: {
					items: 3
				}
			}
		});
	}

	function loadTopCategories(baseUrl, categoryUrl, defaultImage) {
		if (!categoryUrl) {
			return;
		}
		var $list = $("#home-category-list");
		var $loading = $("#home-category-loading");
		if (!$list.length) {
			return;
		}
		$.getJSON(categoryUrl, function (data) {
			var categories = data.results || data;
			categories = Array.isArray(categories) ? categories : [];
			categories.sort(function (a, b) {
				return (b.post_count || 0) - (a.post_count || 0);
			});
			categories = categories.slice(0, 4);

			$list.empty();
			if ($loading.length) {
				$loading.remove();
			}
			if (!categories.length) {
				$list.append($("<div>").addClass("col-12 text-center").text("No categories yet."));
				return;
			}

			categories.forEach(function (category) {
				$list.append(buildCategoryCard(category, baseUrl, defaultImage));
			});
		});
	}

	function loadLatestPosts(postListUrl, blogHomeUrl, defaultImage) {
		var $carousel = $("#latest-posts-carousel");
		var $loading = $("#latest-posts-loading");
		if (!$carousel.length || !postListUrl || !blogHomeUrl) {
			return;
		}
		var apiUrl = postListUrl + "?ordering=-created_date&page_size=6";
		$.getJSON(apiUrl, function (data) {
			var posts = data.results || data;
			posts = Array.isArray(posts) ? posts : [];
			if ($loading.length) {
				$loading.remove();
			}
			if (!posts.length) {
				$carousel.html("<div class=\"col-12 text-center\">No posts yet.</div>");
				return;
			}
			var items = [];
			posts.forEach(function (post) {
				var $card = buildLatestPostCard(post, blogHomeUrl, defaultImage);
				if ($card) {
					items.push($card.prop("outerHTML"));
				}
			});
			$carousel.html(items.join(""));
			initLatestCarousel($carousel, items.length);
		}).fail(function () {
			if ($loading.length) {
				$loading.text("Unable to load latest posts right now.");
			}
		});
	}

	function init() {
		if (!window.jQuery) {
			return;
		}
		var $ = window.jQuery;
		var config = document.getElementById("top-stories-config");
		if (!config) {
			return;
		}
		var postListUrl = config.dataset.postListUrl;
		var blogHomeUrl = config.dataset.blogHomeUrl;
		var categoryUrl = config.dataset.categoryUrl;
		var defaultImage = config.dataset.defaultImage;
		var $list = $("#top-stories-list");
		var $loading = $("#top-stories-loading");

		if (!postListUrl || !blogHomeUrl || !$list.length) {
			return;
		}

		var apiUrl = postListUrl + "?ordering=-counted_view&page_size=6";
		$.getJSON(apiUrl, function (data) {
			var posts = data.results || data;
			posts = Array.isArray(posts) ? posts : [];
			posts.sort(function (a, b) {
				return (b.counted_view || 0) - (a.counted_view || 0);
			});
			posts = posts.slice(0, 3);

			$list.empty();
			if (!posts.length) {
				$list.append($("<div>").addClass("col-12 text-center").text("No stories yet."));
				return;
			}

			posts.forEach(function (post) {
				$list.append(buildTopStoryCard(post, blogHomeUrl, defaultImage));
			});
		}).fail(function () {
			if ($loading.length) {
				$loading.text("Unable to load top stories right now.");
			}
		});

		loadTopCategories(blogHomeUrl, categoryUrl, defaultImage);
		loadLatestPosts(postListUrl, blogHomeUrl, defaultImage);
	}

	window.addEventListener("load", init);
})();
