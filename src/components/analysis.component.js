import React, { Component } from 'react'
import LoggedNavBar from './logged_navbar.component'
import { loginContext } from "../context/LoginContext"
import axios from "axios";
import AnalysisResult from './analysis_result.component'
import BarLoader from "react-spinners/BarLoader";


export default class Analysis extends Component {

  constructor(props){
    super(props)
    this.onFileChange = this.onFileChange.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.getData = this.getData.bind(this);
    this.goBack = this.goBack.bind(this);

    this.resultFlag = false;
    this.result = null;
    this.graphData = [2,6,3,5,5,7,2,6,3,5,5,7,2,6,3,5,5,7,4,5,6]

    this.state = {
      source: 'reddit',
      mode: 'intensity',
      resultFlag: false,
      loading: false,
      error: false,
      flagResults: false,
      selectedFile: null,
    }
  }

  handleChange = e => {
    this.setState({ [e.target.name]: e.target.value})
  }

  onFileChange = event => {
    this.setState({ selectedFile: event.target.files[0] });
  }


  //Sending json to backend and getting analysis
  getData(event){
    this.setState({ loading: true })
    this.setState({ error: false })
    // Create an object of formData
    const formData = new FormData();
    // Update the formData object
    formData.append(
      "file",
      this.state.selectedFile,
      this.state.selectedFile.name
    );
    // Details of the uploaded file
    console.log(this.selectedFile);
    //Avoid refreshing page when clicking button
    event.preventDefault(); 
    // Request made to the backend api
    // Send formData object
    axios.post('/analysis', formData,{
      params: {
        source: this.state.source,
        mode: this.state.mode,
        username: this.context.loggedIn
      },
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    .then((response) => {
      this.result = response.data
      this.resultFlag = true
      this.setState({ flagResults: true}, function () {
        console.log(this.state.flagResults);
      });
      console.log("Response: ",this.result)

    }).catch((error) => {
        if (error.response) {
          console.log(error.response)
          console.log(error.response.status)
          console.log(error.response.headers)
          this.setState({ loading: false })
          this.setState({ error: true })
        }
    }) 
  }

  goBack() {
    this.setState({flagResults: false});
    this.setState({ loading: false });
  }

  render() {
    if(this.state.flagResults){
      return(
        <AnalysisResult 
          statistics={this.result} 
          mode={this.state.mode}
          goBack={this.goBack}
        /> 
      )
    }
    else{
      return(
        <loginContext.Consumer>
          {(context) => {
            if(context.loggedIn){
              return (
                <div className="web-container">
                    <LoggedNavBar 
                      login={context.loggedIn} 
                    />
                    <h3>Analysis</h3>
                    <form>
        
                      <div className="mb-3">
                        <label htmlFor="sourceInput">Source</label>
                        <select onChange={this.handleChange} name="source" id="sourceInput" className="form-select" aria-label="Default select example">
                            <option defaultValue="reddit">Reddit</option>
                            <option value="twitter">Twitter</option>
                        </select>
                      </div>
        
                      <div className="mb-3">
                        <label htmlFor="modeInput">Mode</label>
                        <select onChange={this.handleChange} name="mode" id="modeInput" className="form-select" aria-label="Default select example">
                            <option defaultValue="intensity">Intensity</option>
                            <option value="presence">Relevance</option>
                            
                        </select>
                      </div>
      
                      <div className="mb-3">
                        <input type="file" onChange={this.onFileChange} />
                      </div>
        
                      <div className="d-grid centered-button">
                        <button
                          onClick={this.getData}
                          disabled={this.state.loading || !this.state.selectedFile} // Disable if loading or no file selected
                          className="btn btn-primary"
                        >
                          Analyze
                        </button>
                      </div>
      
                      {this.state.loading ?
                        <BarLoader
                            loading={this.state.loading}
                            className="loading-spinner"
                            size={300}
                            aria-label="Loading Spinner"
                            data-testid="loader"
                        /> :
                        null
                      }
      
                      {this.state.error ?
                        <p className='error'>There was an error during search, please try again</p> :
                        null
                      }
        
                      <div>
                        <p>{this.state.result}</p>
                      </div>
                      
                    </form>
                </div>
              )
        
            }
            else{
              <div>
                <p>In order to search you need to sign-in</p>
                <p>User: {this.context}</p>
              </div>
            }
          }}
        </loginContext.Consumer>
      )

    }

  }
}

Analysis.contextType = loginContext; 