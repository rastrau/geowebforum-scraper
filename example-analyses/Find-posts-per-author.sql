SELECT
	post_author,
	count(*) as posts_count
FROM posts
GROUP BY post_author
ORDER BY posts_count desc;
