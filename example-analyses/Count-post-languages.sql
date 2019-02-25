SELECT
  DISTINCT(post_language),
  count(*)
FROM posts
GROUP BY post_language;
