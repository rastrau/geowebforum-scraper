SELECT
  thread_name,
  thread_id,
  posts_count
FROM threads
JOIN (
 SELECT
 	thread_id,
 	count(*) as posts_count
 	FROM posts
 	GROUP BY thread_id
) using(thread_id)
ORDER BY posts_count desc;
