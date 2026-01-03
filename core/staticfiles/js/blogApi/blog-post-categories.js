window.addEventListener('load', function () {
        if (!window.jQuery) {
            return;
        }
        var listEl = document.getElementById("post-category-list");
        if (!listEl) {
            return;
        }
        var categoryUrl = listEl.dataset.categoryUrl;
        var blogHomeUrl = listEl.dataset.blogHomeUrl;
        var postListUrl = listEl.dataset.postListUrl;
        var pathParts = window.location.pathname.split("/").filter(Boolean);
        var postId = pathParts[pathParts.length - 1];
        var isPostPage = postId && !isNaN(parseInt(postId, 10));
        if (!isPostPage) {
            $.getJSON(categoryUrl, function (data) {
                var categories = data.results || data;
                var $list = $("#post-category-list");
                $list.empty();

                categories.forEach(function (cat) {
                    var link = blogHomeUrl + "?categories=" + encodeURIComponent(cat.id);
                    $list.append(
                        '<li><a href="' + link + '" class="d-flex justify-content-between"><p>' +
                        cat.name +
                        '</p></a></li>'
                    );
                });
            });
            return;
        }

        var postUrl = postListUrl + postId + "/";
        $.getJSON(postUrl, function (data) {
            var categories = Array.isArray(data.categories_info) ? data.categories_info : [];
            if (!categories.length && Array.isArray(data.categories)) {
                categories = data.categories.map(function (name) {
                    return { name: name };
                });
            }
            var $list = $("#post-category-list");
            $list.empty();
            if (!categories.length) {
                $list.append('<li><span>No categories</span></li>');
                return;
            }
            categories.forEach(function (cat) {
                var link = blogHomeUrl;
                if (cat.id) {
                    link += "?categories=" + encodeURIComponent(cat.id);
                }
                $list.append(
                    '<li><a href="' + link + '" class="d-flex justify-content-between"><p>' +
                    (cat.name || "") +
                    '</p></a></li>'
                );
            });
        });
    });
