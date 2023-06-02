import React, { Component } from 'react';
import LoggedNavBar from './logged_navbar.component';
import { loginContext } from "../context/LoginContext";
import axios from "axios";
import AnalysisResult from './analysis_result.component';
import {withRouter} from './withRouter';

class UserOptions extends Component {
  constructor(props) {
    super(props);

    this.handlePasswordChange = this.handlePasswordChange.bind(this);
    this.sendData = this.sendData.bind(this);
    this.logout = this.logout.bind(this);

    this.state = {
      passwordFields: {
        oldPassword: '',
        newPassword1: '',
        newPassword2: ''
      },
      success: false,
      oldPasswordError: false,
      newPasswordError: false
    };
  }

  handlePasswordChange = e => {
    const { name, value } = e.target;
    this.setState(prevState => ({
      passwordFields: {
        ...prevState.passwordFields,
        [name]: value
      }
    }));
  };

  //Sending json to backend and getting analysis
  sendData(event) {
    // Request made to the backend api
    // Send formData object
    axios.put(`/change-password`, {
      username: this.context.loggedIn,
      oldPassword: this.state.passwordFields.oldPassword,
      newPassword1: this.state.passwordFields.newPassword1,
      newPassword2: this.state.passwordFields.newPassword2

    })
      .then((response) => {
        const res = response.data;

        // Reset password fields
        this.setState({
          passwordFields: {
            oldPassword: '',
            newPassword1: '',
            newPassword2: ''
          },
          success: true,
          oldPasswordError: false,
          newPasswordError: false
        });

      })
      .catch((error) => {
        if (error.response) {
          console.log(error.response);
          console.log(error.response.status);
          console.log(error.response.headers);

          if (error.response.data === 'Wrong password') {
            this.setState({
              oldPasswordError: true,
              success: false,
              newPasswordError: false
            });
          }
          else if (error.response.data === 'Passwords do not match') {
            this.setState({
              newPasswordError: true,
              success: false,
              oldPasswordError: false
            });
          }   
        }
      });
  }

  logout() {
    this.context.setLoggedIn('');
    this.props.navigate('/sign-in');
  }

  render() {
    const { oldPassword, newPassword1, newPassword2 } = this.state.passwordFields;
    const isButtonDisabled = !(oldPassword && newPassword1 && newPassword2);    
    
    return(
      <loginContext.Consumer>
        {(context) => {
          if(context.loggedIn){
            return (
              <div className="web-container">
                  <LoggedNavBar 
                    login={context.loggedIn} 
                  />

                  <h2>User: {context.loggedIn}</h2>

                  <div>
                    <h3>Change password</h3>
                    
                    <form>
                      <div className="mb-3">
                        <label>Previous password</label>
                        <input
                            type="password"
                            className="form-control"
                            placeholder="Enter password"
                            name='oldPassword'
                            onChange={this.handlePasswordChange}
                        />
                      </div>

                      <div className="mb-3">
                        <label>New password</label>
                        <input
                            type="password"
                            className="form-control"
                            placeholder="Enter password"
                            name='newPassword1'
                            onChange={this.handlePasswordChange}
                        />
                      </div>

                      <div className="mb-3">
                        <label>Repeat new password</label>
                        <input
                            type="password"
                            className="form-control"
                            placeholder="Enter password"
                            name='newPassword2'
                            onChange={this.handlePasswordChange}
                        />
                      </div>

                      <div className="d-grid">
                        <button 
                          type="button"
                          className="btn btn-primary" 
                          onClick={this.sendData}
                          disabled={isButtonDisabled}>
                            Change password
                        </button>
                      </div>
                    </form>

                    {this.state.success ?
                      <p style={{color:'green'}}>The password was succesfully changed.</p>
                      :
                      <></>
                    }

                    {this.state.oldPasswordError ?
                      <p style={{color:'red'}}>The old password is incorrect.</p>
                      :
                      <></>
                    }

                    {
                      this.state.newPasswordError ?
                      <p style={{color:'red'}}>The new passwords do not match.</p>
                      :
                      <></>
                    }

                  </div>

                  <div className="d-grid" style={{marginTop: '2em'}}>
                    <h3>Log out</h3>
                      <button type="button"className="btn btn-danger" onClick={this.logout}>Log out</button>
                  </div>


                  
                    
              </div>
            )
      
          }
          else{
            <div>
              <p>You need to sign-in</p>
            </div>
          }
        }}
      </loginContext.Consumer>
    )

    

  }
}

export default withRouter(UserOptions);
UserOptions.contextType = loginContext; 