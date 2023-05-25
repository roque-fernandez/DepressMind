import React, { Component } from 'react'
import LoggedNavBar from './logged_navbar.component'
import IntenseSentences from './intense_sentences.component';
import { loginContext } from "../context/LoginContext"
import Plot from 'react-plotly.js';


export default class AnalysisResult extends Component {

  constructor(props){
    super(props)
    this.handleChange = this.handleChange.bind(this);
    this.diagnosis = this.diagnosis.bind(this);
    this.increaseWeekIndex = this.increaseWeekIndex.bind(this);
    this.decreaseWeekIndex = this.decreaseWeekIndex.bind(this);
    this.increaseMonthIndex = this.increaseMonthIndex.bind(this);
    this.decreaseMonthIndex = this.decreaseMonthIndex.bind(this);
    this.increaseDayIndex = this.increaseDayIndex.bind(this);
    this.decreaseDayIndex = this.decreaseDayIndex.bind(this);
    this.getDimensionsEvolutions = this.getDimensionsEvolutions.bind(this);
    this.dateFormat = this.dateFormat.bind(this);
    this.formatDailyStatisticsKeys = this.formatDailyStatisticsKeys.bind(this);
    this.showIntenseSentences = this.showIntenseSentences.bind(this);
    this.goBack = this.goBack.bind(this);
    this.handleGoBack = this.handleGoBack.bind(this);

    //index for the time analysis
    this.monthMaxIndex = Object.keys(this.props.statistics[3]).length - 1;
    this.monthIndex= 0;
    this.weekMaxIndex = Object.keys(this.props.statistics[2]).length - 1;
    this.weekIndex= 0;
    this.dayMaxIndex = Object.keys(this.props.statistics[1]).length - 1;
    this.dayIndex= 0;
    console.log("Month Index:",this.monthIndex)
    console.log("Month MaxIndex:",this.monthMaxIndex)
    console.log("Week Index:",this.weekIndex)
    console.log("Week MaxIndex:",this.weekMaxIndex)
    console.log("Day Index:",this.dayIndex)
    console.log("Day MaxIndex:",this.dayMaxIndex)
    //evolution of the dimensions
    //console.log("STATISTICS: ",this.props.statistics)
    console.log("DailyStatistics:", this.props.statistics[1])
    this.formattedDailyStatistics = this.formatDailyStatisticsKeys(this.props.statistics[1])
    this.formattedDailyStatisticsKeys = Object.keys(this.formattedDailyStatistics).sort()
    console.log("Formatted:",this.formattedDailyStatistics)
    console.log("Formatted keys:",this.formattedDailyStatisticsKeys)
    console.log("Non formatted:",this.props.statistics[1])
    this.dimensionEvolution = this.getDimensionsEvolutions(this.formattedDailyStatistics)
    //most intense sentences
    this.intenseSentences = this.props.statistics[4]
    console.log("Intense sentences:",this.intenseSentences)
    //set title 
    if(this.props.mode === 'presence'){
      this.title = "Ocurrence"
    }
    else{
      this.title = "Intensity"
    }


    this.state = {
      generalStatistics: this.props.statistics[0],
      generalDiagnosis: this.diagnosis(this.props.statistics[0]),
      monthlyStatistics: this.props.statistics[3],
      weeklyStatistics: this.props.statistics[2],
      dailyStatistics: this.props.statistics[1],
      //graph buttons
      monthNextButton: true,
      monthPreviousButton: false,
      weekNextButton: true,
      weekPreviousButton: false,
      dayNextButton: true,
      dayPreviousButton: false,
      //type of time analysis
      timeAnalysis: 'weekly',
      //flag to show intense sentences
      flagIntenseSentences:false
    }
  }

  handleChange = e => {
    this.setState({ [e.target.name]: e.target.value})
  }

  diagnosis(results){
    const total = results.reduce((a, b) => a + b, 0);
    var diagnosis = ""
    if (total >= 1 && total <= 10){
      diagnosis = 'These ups and downs are considered normal'
    }
    else if (total >= 11 && total <= 16){
      diagnosis = "Mild mood disturbance"
    }
    else if (total >= 17 && total <= 20){
      diagnosis = "Borderline clinical depression"
    }
    else if (total >= 21 && total <= 30){
      diagnosis = "Moderate depression"
    }
    else if (total >= 21 && total <= 40){
      diagnosis = "Severe depression"
    }
    else{
      diagnosis = "Extreme depression"
    }
    return diagnosis
  }

  getDimensionsEvolutions(statistics){
    //we want an object where the key is the index of the bdi question
    //the value is the array with the results of dailyStatistics for that question
    //first we sort the keys to access the array in chronological order
    var keys = Object.keys(statistics).sort();
    var result = {}
    const maxIndex = statistics[keys[0]].length
    console.log("keys: ",keys)
    console.log("MaxIndex: ",maxIndex)

    for(let i=0;i < maxIndex;i++){
      console.log("Index: ",i)
      //contains the evolution of one dimension
      let evolutions = []
      keys.forEach( k =>{
        evolutions.push(statistics[k][i])
      })
      result[i] = evolutions
    }
    console.log("Evolutions:",result)
    return result
  }

  dateFormat(str){
    //convert date like (2022,11,7) to (2022,11,07)
    //eliminate spaces and the ()
    str = str.replace(/\s/g, '');
    str = str.slice(1,-1)
    //split the date by , or -
    var [year, month, day] = str.split(/[,-]/)
    var newDay = day
    var newMonth = month
    // console.log("Day:",day)
    // console.log("Len:",day.length)
    if(day.length === 1){
      newDay = '0' + newDay
    }
    if(month.length === 1){
      newMonth = '0' + month
    }
    
    return '(' + year + ',' + newMonth + ',' + newDay + ')'
  }

  formatDailyStatisticsKeys(statistics){
    var keys = Object.keys(statistics);
    var result = {}

    keys.forEach( k =>{
      console.log("k:",k)
      var newKey = this.dateFormat(k)
      console.log("newKey:",newKey)
      result[newKey] = statistics[k]
    })
    return result
  }

  increaseMonthIndex(){
    if (this.monthIndex < this.monthMaxIndex){
      this.monthIndex += 1;
      console.log("Index:",this.monthIndex)
      //next button
      if (this.monthIndex === this.monthMaxIndex){
        this.setState({ monthNextButton: false })
      }
      else{
        this.setState({ monthNextButton: true })
      }
      //previous button
      if(this.monthIndex > 0){
        this.setState({ monthPreviousButton: true })
      }
    }
  }

  decreaseMonthIndex(){
    if (this.monthIndex > 0){
      this.monthIndex -= 1;
      console.log("Index:",this.monthIndex)
      //previous button
      if (this.monthIndex === 0){
        this.setState({ monthPreviousButton: false })
      }
      else{
        this.setState({ monthPreviousButton: true })
      }
      //next button
      if(this.monthIndex < this.monthMaxIndex){
        this.setState({ monthNextButton: true })
      }
    }
  }

  increaseWeekIndex(){
    if (this.weekIndex < this.weekMaxIndex){
      this.weekIndex += 1;
      console.log("Week index:",this.weekIndex)
      //next button
      if (this.weekIndex === this.weekMaxIndex){
        this.setState({ weekNextButton: false })
      }
      else{
        this.setState({ weekNextButton: true })
      }
      //previous button
      if(this.weekIndex > 0){
        this.setState({ weekPreviousButton: true })
      }
    }
  }

  decreaseWeekIndex(){
    if (this.weekIndex > 0){
      this.weekIndex -= 1;
      console.log("Week index:",this.weekIndex)
      //previous button
      if (this.weekIndex === 0){
        this.setState({ weekPreviousButton: false })
      }
      else{
        this.setState({ weekPreviousButton: true })
      }
      //next button
      if(this.weekIndex < this.weekMaxIndex){
        this.setState({ weekNextButton: true })
      }
    }
  }

  increaseDayIndex(){
    if (this.dayIndex < this.dayMaxIndex){
      this.dayIndex += 1;
      console.log("Index:",this.dayIndex)
      //next button
      if (this.dayIndex === this.dayMaxIndex){
        this.setState({ dayNextButton: false })
      }
      else{
        this.setState({ dayNextButton: true })
      }
      //previous button
      if(this.dayIndex > 0){
        this.setState({ dayPreviousButton: true })
      }
    }
  }

  decreaseDayIndex(){
    if (this.dayIndex > 0){
      this.dayIndex -= 1;
      console.log("Index:",this.dayIndex)
      //previous button
      if (this.dayIndex === 0){
        this.setState({ dayPreviousButton: false })
      }
      else{
        this.setState({ dayPreviousButton: true })
      }
      //next button
      if(this.dayIndex < this.dayMaxIndex){
        this.setState({ dayNextButton: true })
      }
    }
  }

  showIntenseSentences(){
    this.setState({ flagIntenseSentences: true })
  }

  goBack() {
    this.setState({flagIntenseSentences: false});
  }
  
  //to analyze again
  handleGoBack() {
    this.props.goBack(); // call the goBack function passed as a prop
  }

  render() {
    const colors = [
      "rgba(255, 195, 0, 1)", // color for y-value = 1
      "rgba(255, 123, 0, 1)", // color for y-value = 2
      "red" // color for y-value = 3
    ];

    const BDITitles = ['Sadness','Pessimism','Past Failure','Loss of Pleasure','Guilty Feelings','Punishment Feelings','Self-Dislike','Self-Criticalness','Suicidal Thoughts or Wishes','Crying','Agitation','Loss of Interest','Indecisiveness','Worthlessness','Loss of Energy','Changes in Sleeping Pattern','Irritability','Changes in Appetite','Concentration Difficulty','Tiredness or Fatigue','Loss of Interest in Sex'];

    if(this.context.loggedIn ){
      if(this.state.flagIntenseSentences){
        return(
          <IntenseSentences 
            sentences = {this.intenseSentences} 
            analysis = {this.state.generalStatistics}
            goBack={this.goBack} 
          />
        )
      }
      return (
        <div className="web-container">
            <LoggedNavBar/>  

            <div style={{marginTop: '1em',marginBottom: '2em'}} className="d-grid centered-button">
                <button onClick={this.handleGoBack} className="btn btn-outline-primary">
                  Analyze again
                </button>
            </div> 

            <div className="mb-3">
        
              {
                this.props.mode === 'intensity' ?

                <div style={{textAlign: 'center'}}>
                  <h1>{this.title} analysis</h1>
                
                  <h5>Diagnosis: {this.state.generalDiagnosis}</h5>

                  <Plot
                    data={[
                      {
                        x: BDITitles,
                        y: this.state.generalStatistics,
                        type: 'bar',
                        marker: {
                          color: this.state.generalStatistics.map((val) => colors[val-1]) // Map values to corresponding colors
                        }
                        
                      }
                    ]}
                    layout={ {
                      width: 550, 
                      height: 440, 
                      title: this.state.mode,
                      yaxis: {
                        tickmode: 'linear',
                        dtick: 1,
                        // Add any other y-axis formatting options here
                      }
                    }}
                  />

                  <div style={{marginTop: '1.5em',marginBottom: '1em'}} className="d-grid centered-button">
                    <button onClick={this.showIntenseSentences} className="btn btn-primary">
                      Show evidence
                    </button>
                  </div>

                </div>

                :
                null
              }

              {
                this.props.mode === 'presence' ?
                <div>
                  <div style={{textAlign: 'center'}}>
                    <h1>Depression symptoms relevance</h1>
                  </div>
                  <Plot
                    data={[
                      {
                        x: ['Sadness','Pessimism','Past Failure','Loss of Pleasure','Guilty Feelings','Punishment Feelings','Self-Dislike','Self-Criticalness','Suicidal Thoughts or Wishes','Crying','Agitation','Loss of Interest','Indecisiveness','Worthlessness','Loss of Energy','Changes in Sleeping Pattern','Irritability','Changes in Appetite','Concentration Difficulty','Tiredness or Fatigue','Loss of Interest in Sex'],
                        y: this.state.generalStatistics,
                        type: 'bar',
                        
                      }
                    ]}
                    layout={ 
                      {
                        width: 550, 
                        height: 440, 
                        title: this.state.mode,
                        yaxis: {
                          range: [0, 1],
                          tickformat: ',.0%' // format tick labels as percentages
                        } 
                      }
                    }
                  />
                </div>
                :
                null
              }     

            </div>

            <div className="mb-3">
              <h3>Temporal analysis</h3>
              <select className="form-select" id="typeInput" name="timeAnalysis" onChange={this.handleChange} aria-label="Default select example">
              <option defaultValue="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="daily">Daily</option>
              </select>
            </div>

             {/* RELEVANCE TEMPORAL ANALYSIS */} 
            {
              this.props.mode === 'presence' ?

              <div>
                {
                  this.state.timeAnalysis === 'weekly' ?

                  <div className="mb-3">                
                    <Plot
                      data={[
                        {
                          x: BDITitles,
                          y: Object.values(this.state.weeklyStatistics)[this.weekIndex],
                          type: 'bar'
                        }
                      ]}
                      layout={ 
                        {
                          width: 550, 
                          height: 440, 
                          title: "(Year,week)\n" + Object.keys(this.state.weeklyStatistics)[this.weekIndex],
                          yaxis: {
                            range: [0, 1],
                            tickformat: ',.0%'
                          }
                        } 
                      }
                    />

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <button onClick={this.decreaseWeekIndex} disabled={!this.state.weekPreviousButton} className="btn btn-primary">
                      Previous week
                    </button>

                    <button onClick={this.increaseWeekIndex} disabled={!this.state.weekNextButton} className="btn btn-primary">
                      Next week
                    </button>

                  </div>              
                </div>
                :
                <></>
                }

                {
                  this.state.timeAnalysis === 'monthly' ?

                <div className="mb-3">                
                  <Plot
                    data={[
                      {
                        x: BDITitles,
                        y: Object.values(this.state.monthlyStatistics)[this.monthIndex],
                        type: 'bar',
                        marker: {
                          color: Object.values(this.state.monthlyStatistics)[this.monthIndex].map((val) => colors[val-1]) // Map values to corresponding colors
                        }
                      }
                    ]}
                    layout={ 
                      {
                        width: 550, 
                        height: 440, 
                        title: "(Year,month)\n" + Object.keys(this.state.monthlyStatistics)[this.monthIndex],
                        yaxis: {
                          range: [0, 1],
                          tickformat: ',.0%'
                        }
                      } 
                    }
                  />

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <button onClick={this.decreaseMonthIndex} disabled={!this.state.monthPreviousButton} className="btn btn-primary">
                      Previous month
                    </button>

                    <button onClick={this.increaseMonthIndex} disabled={!this.state.monthNextButton} className="btn btn-primary">
                      Next month
                    </button>
                  </div>              
                </div>
                :
                <></>
                }

                {
                  this.state.timeAnalysis === 'daily' ?

                <div className="mb-3">                
                  <Plot
                    data={[
                      {
                        x: BDITitles,
                        y: Object.values(this.state.dailyStatistics)[this.dayIndex],
                        type: 'bar',
                        marker: {
                          color: Object.values(this.state.dailyStatistics)[this.dayIndex].map((val) => colors[val-1]) // Map values to corresponding colors
                        }
                      }
                    ]}
                    layout={ 
                      {
                        width: 550, 
                        height: 440, 
                        title: "(Year,month,day)\n" + Object.keys(this.state.dailyStatistics)[this.dayIndex],
                        yaxis: {
                          range: [0, 1],
                          tickformat: ',.0%'
                        }
                      } 
                    }
                  />

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <button onClick={this.decreaseDayIndex} disabled={!this.state.dayPreviousButton} className="btn btn-primary">
                      Previous day
                    </button>

                    <button onClick={this.increaseDayIndex} disabled={!this.state.dayNextButton} className="btn btn-primary">
                      Next day
                    </button>
                  </div>              
                </div>
                :
                <></>
                }
              </div>

              :
              null
            }


            {/* INTENSITY TEMPORAL ANALYSIS */}
            {
              this.props.mode === 'intensity' ?

              <div>
                {
                  this.state.timeAnalysis === 'weekly' ?

                  <div className="mb-3">                
                    <Plot
                      data={[
                        {
                          x: BDITitles,
                          y: Object.values(this.state.weeklyStatistics)[this.weekIndex],
                          type: 'bar'
                        }
                      ]}
                      layout={ 
                        {
                          width: 550, 
                          height: 440, 
                          title: "(Year,week)\n" + Object.keys(this.state.weeklyStatistics)[this.weekIndex],
                          yaxis: {
                            tickmode: 'linear',
                            dtick: 1,
                            tickformat: ',.0%'
                            // Add any other y-axis formatting options here
                          }
                        } 
                      }
                    />

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <button onClick={this.decreaseWeekIndex} disabled={!this.state.weekPreviousButton} className="btn btn-primary">
                      Previous week
                    </button>

                    <button onClick={this.increaseWeekIndex} disabled={!this.state.weekNextButton} className="btn btn-primary">
                      Next week
                    </button>

                  </div>              
                </div>
                :
                <></>
                }

                {
                  this.state.timeAnalysis === 'monthly' ?

                <div className="mb-3">                
                  <Plot
                    data={[
                      {
                        x: BDITitles,
                        y: Object.values(this.state.monthlyStatistics)[this.monthIndex],
                        type: 'bar'
                      }
                    ]}
                    layout={ 
                      {
                        width: 550, 
                        height: 440, 
                        title: "(Year,month)\n" + Object.keys(this.state.monthlyStatistics)[this.monthIndex],
                        yaxis: {
                          tickmode: 'linear',
                          dtick: 1,
                          tickformat: ',.0%'
                          // Add any other y-axis formatting options here
                        }
                      } 
                    }
                  />

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <button onClick={this.decreaseMonthIndex} disabled={!this.state.monthPreviousButton} className="btn btn-primary">
                      Previous month
                    </button>

                    <button onClick={this.increaseMonthIndex} disabled={!this.state.monthNextButton} className="btn btn-primary">
                      Next month
                    </button>
                  </div>              
                </div>
                :
                <></>
                }

                {
                  this.state.timeAnalysis === 'daily' ?

                <div className="mb-3">                
                  <Plot
                    data={[
                      {
                        x: BDITitles,
                        y: Object.values(this.state.dailyStatistics)[this.dayIndex],
                        type: 'bar',
                        marker: {
                          color: Object.values(this.state.dailyStatistics)[this.dayIndex].map((val) => colors[val-1]) // Map values to corresponding colors
                        }
                      }
                    ]}
                    layout={ 
                      {
                        width: 550, 
                        height: 440, 
                        title: "(Year,month,day)\n" + Object.keys(this.state.dailyStatistics)[this.dayIndex],
                        yaxis: {
                          tickmode: 'linear',
                          dtick: 1,
                          tickformat: ',.0%'
                          // Add any other y-axis formatting options here
                        }
                      } 
                    }
                  />

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <button onClick={this.decreaseDayIndex} disabled={!this.state.dayPreviousButton} className="btn btn-primary">
                      Previous day
                    </button>

                    <button onClick={this.increaseDayIndex} disabled={!this.state.dayNextButton} className="btn btn-primary">
                      Next day
                    </button>
                  </div>              
                </div>
                :
                <></>
                }
              </div>
              :
              null
            }
 
            {/* DIMENSION EVOLUTIONS */}

            <div className="mb-3">                    
              
              <Plot
                data={[
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[0],
                    type: 'scatter',
                    name: 'Sadness'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[1],
                    type: 'scatter',
                    name: 'Pessimism'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[2],
                    type: 'scatter',
                    name: 'Past failure'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[3],
                    type: 'scatter',
                    name: 'Loss of Pleasure'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[4],
                    type: 'scatter',
                    name: 'Guilty Feelings'
                  }
                ]}
                layout={ 
                  
                  {
                    width: 550, 
                    height: 440, 
                    //title: "",
                    xaxis: {
                      categoryorder: "array",
                      categoryarray: Object.keys(this.formattedDailyStatistics).sort()
                    }
                  }
                  
                }
              />  

              <Plot
                data={[
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[5],
                    type: 'scatter',
                    name: 'Punishment Feelings'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[6],
                    type: 'scatter',
                    name: 'Self-Dislike'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[7],
                    type: 'scatter',
                    name: 'Self-Criticalness'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[8],
                    type: 'scatter',
                    name: 'Suicidal Thoughts or Wishes'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[9],
                    type: 'scatter',
                    name: 'Crying'
                  }
                ]}
                layout={ 
                  {
                    width: 550, 
                    height: 440, 
                    //title: ""
                  } 
                }
              /> 

              <Plot
                data={[
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[10],
                    type: 'scatter',
                    name: 'Agitation'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[11],
                    type: 'scatter',
                    name: 'Loss of Interest'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[12],
                    type: 'scatter',
                    name: 'Indecisiveness'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[13],
                    type: 'scatter',
                    name: 'Worthlessness'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[14],
                    type: 'scatter',
                    name: 'Loss of Energy'
                  }
                ]}
                layout={ 
                  {
                    width: 550, 
                    height: 440, 
                    //title: ""
                  } 
                }
              />  

              <Plot
                data={[
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[15],
                    type: 'scatter',
                    name: 'Changes in Sleeping Pattern'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[16],
                    type: 'scatter',
                    name: 'Irritability'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[17],
                    type: 'scatter',
                    name: 'Changes in Appetite'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[18],
                    type: 'scatter',
                    name: 'Concentration Difficulty'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[19],
                    type: 'scatter',
                    name: 'Tiredness or Fatigue'
                  },
                  {
                    x: Object.keys(this.formattedDailyStatistics).sort(),
                    y: this.dimensionEvolution[20],
                    type: 'scatter',
                    name: 'Loss of Interest in Sex'
                  }
                ]}
                layout={ 
                  {
                    width: 550, 
                    height: 440, 
                    //title: ""
                  } 
                }
              />  

            </div>
            

          
              
        </div>

        
      )
    }
    else{
      <div>
        <p>In order to search you need to sign-in</p>
        <p>User: {this.context}</p>
    </div>
    }
  }
}

AnalysisResult.contextType = loginContext; 