The plan is to make a web application where the user can draw images and share them on a public page any user can access. Users can then give feedback on the images in the form of text replies as well as upvotes and downvotes. The main page will list posted images and the user can choose between seeing recent posts or most upvoted posts.

The images will be draw in an editor page, which consists of a grid of pixels, which can be colored in by clicking them. The color is chosen with color codes and the images will be pixel art size, which means that they will not be very large (about 64 x 64 pixels).

In other words the application will function as a platform for creating and sharing pixel art.

The database will consist of the following tables:
- Users: Username/email and password.
- Images: All images, including not shared ones.
- Replies: Text replies to images.
- Likes: Likes to images.
- Editor: A table containing data for unfinished pictures. This will allow users to take a break and continue drawing pictures later where they left off.

I am not yet completely sure how to properly store the images. Storing the images as files and store their file location in the database allows for easy displaying of the images aswell as smaller space complexity. Storing the images directly in the database may allow easier editing of the images, but it will take up more space and will be more problematic to display. I will begin by storing unfinished images in the database and the already posted ones as files to more easily display them.