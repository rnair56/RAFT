import axios from "axios";
import React from "react";
import { withRouter  } from "react-router-dom";

const ChatroomPage = ({ match, socket }) => {
  const chatroomId = match.params.id;
  const [messages, setMessages] = React.useState([]);
  const messageRef = React.useRef();
  const [userId, setUserId] = React.useState("");
  // const [oldMessages,setOldMessages] = React.useState([]);
  // const {roomid} = useParams();

  console.log(match.params.id)
  

  const sendMessage = () => {
    if (socket) {
      socket.emit("chatroomMessage", {
        chatroomId,
        message: messageRef.current.value,
      });

      messageRef.current.value = "";
    }
  };


  React.useEffect(() => {
    const token = localStorage.getItem("CC_Token");
    if (token) {
      const payload = JSON.parse(atob(token.split(".")[1]));
      setUserId(payload.id);
    }

    axios
    .get(`http://localhost:8000/chatroom/${chatroomId}`, {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("CC_Token"),
      },
    })
    .then((response) => {
      // setChatrooms(response.data);
      // console.log(response.data);
      const oldMessagesFromDb = response.data.message
      // console.log(oldMessages)
      console.log(oldMessagesFromDb)
      // console.log(oldMessagesFromDb)
      // setMessages(oldMessagesFromDb)
      // localStorage.setItem('roomid', response.data.data.id)
    })
    .catch((err) => {
      // setTimeout(getChatrooms, 3000);
      console.log(err)
    });


    if (socket) {
      socket.on("newMessage", (message) => {
        console.log(message)
        const newMessages = [...messages, message];
        setMessages(newMessages);
      });
    }
    //eslint-disable-next-line
  }, [messages]);

  React.useEffect(() => {
    if (socket) {
      socket.emit("joinRoom", {
        chatroomId,
      });
    }

    return () => {
      //Component Unmount
      if (socket) {
        socket.emit("leaveRoom", {
          chatroomId,
        });
      }
    };
    //eslint-disable-next-line
  }, []);

  return (
    <div className="chatroomPage">
      <div className="chatroomSection">
        <div className="cardHeader">Chatroom Name</div>
        <div className="chatroomContent">
          {messages.map((message, i) => (
            <div key={i} className="message">
              <span
                className={
                  userId === message.userId ? "ownMessage" : "otherMessage"
                }
              >
                {message.name}:
              </span>{" "}
              {message.message}
            </div>
          ))}
        </div>
        <div className="chatroomActions">
          <div>
            <input
              type="text"
              name="message"
              placeholder="Say something!"
              ref={messageRef}
            />
          </div>
          <div>
            <button className="join" onClick={sendMessage}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default withRouter(ChatroomPage);