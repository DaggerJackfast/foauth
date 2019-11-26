import React, { Component } from 'react';
import './App.css';
import FacebookLogin from 'react-facebook-login';
import GoogleLogin from 'react-google-login';
import TwitterLogin from 'react-twitter-auth';
import axios from 'axios';
import { DEV_BACK_URL, GOOGLE_CLIENT_ID, FACEBOOK_CLIENT_ID } from "./config";

class App extends Component {
  onFacebookSuccess = (response) => {
    console.log(response);
    // axios.post(`${DEV_BACK_URL}/api/client-flow/facebook-login`, response)
    //   .then(res => {
    //     console.log('response: ', res);
    //     console.log('response data: ', res.data);
    //   });
  }
  onGoogleSuccess = (response) => {
    console.log(response)
    axios.post(`${DEV_BACK_URL}/api/client-flow/google-login`, response)
      .then(res => {
        console.log('response: ', res);
        console.log('response data: ', res.data);
      });
  }
  onGoogleFailure = (response) => {
    console.log(response);
  }
  onTwitterFailure = (response) => {
    console.log("twitter response", response);
  }
  onTwitterSuccess = (response) => {
    response.json().then(user => {
      console.log('user: ', user);
    })
  }
  render() {   
    const {onFacebookSuccess,onGoogleFailure, onGoogleSuccess, onTwitterFailure, onTwitterSuccess} = this;
    const twitterLoginUrl = `${DEV_BACK_URL}/api/client-flow/twitter-login`;
    const twitterLoginUrlRequest = `${twitterLoginUrl}/request`
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
                  loginUrl={twitterLoginUrl}
                  onFailure={onTwitterFailure}
                  onSuccess={onTwitterSuccess}
                  requestTokenUrl={twitterLoginUrlRequest}
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
              <div>
                <a href={`${DEV_BACK_URL}/api/server-flow/twitter-login`}>TWITTER LOGIN</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
