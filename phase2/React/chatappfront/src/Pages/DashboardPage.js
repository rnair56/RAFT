import React, { useEffect} from "react";
import axios from "axios";
import { Link, NavLink } from "react-router-dom";
// import {NavLink} from "react-router-dom";
// import { Redirect } from "react-router/cjs/react-router.min";

const DashboardPage = (props) => {
  const [chatrooms, setChatrooms] = React.useState([]);
  const [newChatRoomName, setNewChatRoomName] = React.useState('');

  //const history = useHistory()


  useEffect(() => {
    getChatrooms();
     }, []);


  //console.log("history")
  //console.log(history)
  const chatroomNameHandler = (ev) =>{
    setNewChatRoomName(ev.target.value)
  }

  const formHandler = (ev) =>{
    ev.preventDefault()
    console.log(newChatRoomName)
    axios
    .post("http://localhost:8000/chatroom",{name:newChatRoomName}, {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("CC_Token"),
      }
    })
    .then((response) => {
      // setChatrooms(response.data);
      console.log(response.data.message._id);
      //let link = "/chatroom/" + response.data.message._id
      // console.log(link)
     // props.history.push(link)
      // return <Navigate to="/chatroom" />;

      //  localStorage.setItem('roomid',response.data.data.id)
      // this.context.router.history.push(link)
      // return(<Redirect to={link}/>)
    
    })
    .catch((err) => {
      console.log(err)
      // setTimeout(getChatrooms, 3000);
    });

  }
  const getChatrooms = () => {
    axios
      .get("http://localhost:8000/chatroom", {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("CC_Token"),
        },
      })
      .then((response) => {
        setChatrooms(response.data);
        console.log(response.data);
         localStorage.setItem('roomid',response.data.data.id)
      })
      .catch((err) => {
        setTimeout(getChatrooms, 3000);
      });
  }; 
  

 
  return (
    <div className="card">
      <div className="cardHeader">Chatrooms</div>
      <form onSubmit={formHandler}>
      <div className="cardBody">
        <div className="inputGroup">
          <label htmlFor="chatroomName">Chatroom Name</label>
          <input
            type="text"
            value={newChatRoomName}
            onChange={chatroomNameHandler}
            name="chatroomName"
            id="chatroomName"
            placeholder="ChatterBox"
          />
        </div>
        <button type="submit">Create Chatroom</button>
      </div>
      
      </form>
      <div className="chatrooms">
        {chatrooms.map((chatroom) => (
          <div key={chatroom._id} className="chatroom">
            <div>{chatroom.name}</div>
            <Link to={"/chatroom/" + chatroom._id}>
              <div className="join">Join</div>
            </Link>
          </div>
        ))}
      </div>
      <NavLink exact to="/login">
        <button style={{width:270}}type="button" className="logout">logout</button>
        </NavLink>

    </div>
  );
};

export default DashboardPage;


