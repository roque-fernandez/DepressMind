import React, { Component } from 'react'
import LoggedNavBar from './logged_navbar.component'
import { loginContext } from "../context/LoginContext"
import SentenceTable from "./sentence_table.component";

export default class IntenseSentences extends Component {

  constructor(props){
    super(props)
    this.handleChange = this.handleChange.bind(this);

    console.log("Sentences:\n",this.props.sentences);
    console.log("Analysis:\n",this.props.analysis);
    //split indexes of dimensions in two groups depending on the points
    this.zeroIndexes = [];
    this.nonZeroIndexes = [];
    this.splitIndexes(this.props.analysis);
    console.log("Zero indexes: ",this.zeroIndexes);
    console.log("Non Zero indexes: ",this.nonZeroIndexes);
    this.BDITitles = ['Sadness','Pessimism','Past Failure','Loss of Pleasure','Guilty Feelings','Punishment Feelings','Self-Dislike','Self-Criticalness','Suicidal Thoughts or Wishes','Crying','Agitation','Loss of Interest','Indecisiveness','Worthlessness','Loss of Energy','Changes in Sleeping Pattern','Irritability','Changes in Appetite','Concentration Difficulty','Tiredness or Fatigue','Loss of Interest in Sex'];

    
    
    this.state = {
      
    }
  }

  splitIndexes(array){
    array.reduce((acc, cur, index) => {
        if (cur === 0) {
            this.zeroIndexes.push(index);
        } else {
            this.nonZeroIndexes.push(index);
        }
      }, []);

  }

  handleChange = e => {
    this.setState({ [e.target.name]: e.target.value})
  }


  render() {
    if(this.context.loggedIn ){
      return (
        <div className="web-container">
            <LoggedNavBar/>
            <h1>Most intense sentences</h1>

            <div>
              {this.nonZeroIndexes.map((i) => (
                  <>
                    <SentenceTable key={i} title={this.BDITitles[i]} data={this.props.sentences[i]} points={this.props.analysis[i]}/>
                  </>
              ))}
                
            </div>

            <div style={{marginTop: '2em'}}>
                <h6>The following dimensions do not score</h6>
                <div>
                    {this.zeroIndexes.map((i) => (
                        <p key={i}>{this.BDITitles[i]}</p>
                    ))}
                </div>
            </div>

            

        </div>

           
           

        
      )
    }
    else{
      <div>
        <p>In order to search you need to sign-in</p>
    </div>
    }
  }
}

IntenseSentences.contextType = loginContext; 