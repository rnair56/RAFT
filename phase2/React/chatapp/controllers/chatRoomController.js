const mongoose = require("mongoose");
const Chatroom = mongoose.model("Chatroom");
// const Messages = mongoose.model("Messages");
const Message = mongoose.model("Message");

exports.createChatroom = async (req, res) => {
  const { name } = req.body;

  const nameRegex = /^[A-Za-z\s]+$/;

  if (!nameRegex.test(name)) throw "Chatroom name can contain only alphabets.";

  const chatroomExists = await Chatroom.findOne({ name });

  if (chatroomExists) throw "Chatroom with that name already exists!";

  const chatroom = new Chatroom({
    name,
  });

  chatroom.save(function(err,room) {
    res.json({
      message: room,
    });
 })
  // chatroom.
  // res.json({
  //   message: "Chatroom created!",
  // });
};

exports.getAllChatrooms = async (req, res) => {
  const chatrooms = await Chatroom.find({});
  res.json(chatrooms);
};

exports.getChats = async (req, res) => {

  const messages = await Message.find({chatroom:req.params.id});
  if (!messages) throw "Invalid id";
  // res.json('ss');
  res.json({
    message: messages,
  });
};