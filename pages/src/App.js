import React, { Component } from 'react';
import './App.css';
import FacebookLogin from 'react-facebook-login';
import GoogleLogin from 'react-google-login';

const DEV_BACK_URL="https://localhost:5000"

class App extends Component {
  render() {
    const responseFacebook = (response) => {
      console.log(response);
    }

    const responseGoogle = (response) => {
      console.log(response);
    }

    return (
      <div className="App">
        <h1>LOGIN WITH FACEBOOK AND GOOGLE</h1>
        <div className="container">


          <div className="box">
            <div className="box-item">
              Client side flow
              <div>
                <FacebookLogin
                  appId=""
                  fields="name,email,picture"
                  autoLoad={false}
                  redirectUri="https://localhost:3000"
                  callback={responseFacebook}
                />
              </div>
              <div>
                <GoogleLogin
                  clientId=""
                  buttonText="LOGIN WITH GOOGLE"
                  uxMode="redirect"
                  redirectUri="https://localhost:3000"
                  onSuccess={responseGoogle}
                  onFailure={responseGoogle}
                />
              </div>
            </div>
            <div className="box-item">
              Link redirect flow
              <div>
                <a href="https://www.facebook.com/dialog/oauth/?client_id=<clientid>&redirect_uri=https://localhost:3000scope=name,email,picture">LOGIN!</a>
              </div>
              <div>

              </div>
            </div>
            <div className="box-item">
              Server side flow
              <div>
                <a href={`${DEV_BACK_URL}/api/server-flow/google-login`}>GOOGLE LOGIN</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
