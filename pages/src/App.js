import React, { Component } from 'react';
import './App.css';
import FacebookLogin from 'react-facebook-login';
import GoogleLogin from 'react-google-login';
import TwitterLogin from 'react-twitter-auth';
import axios from 'axios';
import { DEV_BACK_URL, GOOGLE_CLIENT_ID, FACEBOOK_CLIENT_ID } from "./config";

class App extends Component {
  render() {
    const onFacebookSuccess = (response) => {
      console.log(response);
    }
    const onGoogleSuccess = (response) => {
      console.log(response);
      // axios.post(`${DEV_BACK_URL}/api/client-flow/google-login`, response)
      //   .then(res => {
      //     console.log('response: ', res);
      //     console.log('response data: ', response.data);
      //   });
    }
    const onGoogleFailure = (response) => {
      console.log(response);
    }
    const onTwitterFailed = (response) => {
      console.log(response);
    }
    const onTwitterSuccess = (response) => {
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
                  appId={FACEBOOK_CLIENT_ID}
                  fields="name,email,picture"
                  autoLoad={false}
                  redirectUri="https://localhost:3000"
                  callback={onFacebookSuccess}
                />
              </div>
              <div>
                <GoogleLogin
                  clientId={GOOGLE_CLIENT_ID}
                  buttonText="LOGIN WITH GOOGLE"
                  redirectUri="https://localhost:3000"
                  onSuccess={onGoogleSuccess}
                  onFailure={onGoogleFailure}
                />
              </div>
              <div>
                <TwitterLogin
                  loginUrl="https://localhost:3000"
                  onFailure={this.onTwitterFailed}
                  onSuccess={this.onTwitterSuccess}
                  requestTokenUrl="https://localhost:3000"
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
              <div>
                <a href={`${DEV_BACK_URL}/api/server-flow/facebook-login`}>FACEBOOK LOGIN</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
