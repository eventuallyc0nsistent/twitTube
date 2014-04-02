--
-- List of videos posted by user = 1 (i.e MyVideos..should not contain post video i.e reply video)
--
select videoid, url 
FROM videos 
where videoid in (
					SELECT videoid 
					FROM user_video 
					WHERE userid = '1' 
						  and user_video_id 
						  not in (
						  			select from_user_vid_id 
						  			from video_post
						  		)
				)

--
-- List of ALL videos(should not contain post video i.e reply video)
--

select videoid, url 
FROM videos 
where videoid in (
					SELECT videoid 
					FROM user_video 
					WHERE user_video_id 
					not in (
								select from_user_vid_id 
								from video_post
						   )
				)


--
-- List of posts containing userid and videoid to each video posted by userid 1
--
SELECT userid, videoid
FROM  user_video 
WHERE user_video_id
					IN (

							SELECT from_user_vid_id
							FROM  video_post 
							WHERE to_user_vid_id
							IN (

									SELECT user_video_id
									FROM  user_video 
									WHERE userid =  '1'
									AND videoid =  '1'
								)
						)
--
-- Click on upload video:
--
$url = video_url;
INSERT INTO videos (videoid, url) VALUES (NULL, video_url);
SELECT videoid FROM videos WHERE url = $url
INSERT INTO user_video (user_video_id, userid, videoid) VALUES (NULL, '1', videoid);

--
-- Click on reply video:
--
$url = video_url;
INSERT INTO videos (videoid, url) VALUES (NULL, video_url);
SELECT videoid FROM videos WHERE url = $url
INSERT INTO user_video (user_video_id, userid, videoid) VALUES (NULL, '1', videoid);
SELECT user_video_id FROM user_video WHERE userid = 1 and videoid = $videoid 
INSERT INTO video_post (postid, to_user_vid_id, from_user_vid_id, timestamp) VALUES (NULL, reply_video_id, $user_video_id, CURRENT_TIMESTAMP);