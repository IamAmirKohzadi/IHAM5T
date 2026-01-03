window.addEventListener('load', function () {
        if (!window.jQuery) {
            return;
        }
        var widget = document.getElementById("top-author-widget");
        if (!widget) {
            return;
        }
        var topAuthorUrl = widget.dataset.topAuthorUrl;
        var defaultImage = widget.dataset.defaultImage;

        $.getJSON(topAuthorUrl, function (data) {
            if (!data || !data.author_name) {
                $("#top-author-name").text("");
                $("#top-author-title").text("We have no chosen blogger this month.");
                $("#top-author-stats").text("");
                $("#top-author-desc").text("");
                $("#top-author-image").attr("src", defaultImage);
                $(".social-links").hide();
                return;
            }

            $(".social-links").show();

            var imageUrl = data.author_image ? data.author_image : defaultImage;

            $("#top-author-name").text(data.author_name);
            $("#top-author-image").attr("src", imageUrl);

            var statsText = "Top author: " + (data.total_views || 0) + " views in last " + (data.period_days || 30) + " days";
            if (data.post_count !== undefined) {
                statsText += " (" + data.post_count + " posts)";
            }
            $("#top-author-stats").text(statsText);

            var desc = data.author_description ? data.author_description : "No bio yet!";
            $("#top-author-desc").text(desc);

            var links = data.social_links || {};
            setSocialLink("#top-author-facebook", links.facebook);
            setSocialLink("#top-author-twitter", links.twitter);
            setSocialLink("#top-author-github", links.github);
            setSocialLink("#top-author-behance", links.behance);
        });
    });

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
