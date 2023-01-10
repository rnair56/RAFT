const router = require("express").Router();
const { catchErrors } = require("../errorHandlers/errorHandler");
const chatroomController = require("../controllers/chatRoomController");

const auth = require("../middlewares/auth");
router.get("/:id",auth, catchErrors(chatroomController.getChats));

router.get("/", auth, catchErrors(chatroomController.getAllChatrooms));
router.post("/", auth, catchErrors(chatroomController.createChatroom));

module.exports = router;