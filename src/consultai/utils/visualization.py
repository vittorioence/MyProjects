"""
Visualization utilities for ConsultAI.
These utilities generate visual representations of deliberation processes and results.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class DeliberationVisualizer:
    """
    Generates visual representations of deliberation processes and results.
    """
    
    def __init__(self, output_dir: str = "output/visualizations"):
        """
        Initialize the deliberation visualizer.
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_html_report(
        self,
        deliberation_results: Dict[str, Any],
        case_study: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate an HTML report of deliberation results.
        
        Args:
            deliberation_results: Dictionary containing deliberation results
            case_study: Case study text
            output_filename: Output filename (optional)
            
        Returns:
            Path to the generated HTML file
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"deliberation_report_{timestamp}.html"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Extract data for visualization
        case_summary = deliberation_results.get("case_summary", {})
        agent_responses = deliberation_results.get("agent_responses", [])
        final_consensus = deliberation_results.get("final_consensus", {})
        performance = deliberation_results.get("performance_scores", {})
        
        # Group responses by role
        responses_by_role = {}
        for response in agent_responses:
            role = response.get("role", "unknown")
            if role not in responses_by_role:
                responses_by_role[role] = []
            responses_by_role[role].append(response)
        
        # Generate HTML content
        html_content = self._generate_html_content(
            case_study=case_study,
            case_summary=case_summary,
            responses_by_role=responses_by_role,
            final_consensus=final_consensus,
            performance=performance
        )
        
        # Write HTML to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report: {output_path}")
        return output_path
    
    def generate_agreement_matrix(
        self,
        deliberation_results: Dict[str, Any],
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate an agreement matrix visualization.
        
        Args:
            deliberation_results: Dictionary containing deliberation results
            output_filename: Output filename (optional)
            
        Returns:
            Path to the generated HTML file
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"agreement_matrix_{timestamp}.html"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Extract agent responses
        agent_responses = deliberation_results.get("agent_responses", [])
        
        # Extract roles
        roles = set()
        for response in agent_responses:
            roles.add(response.get("role", "unknown"))
        roles = list(roles)
        
        # Generate similarity matrix data
        # This is a placeholder - in a real implementation, would calculate actual similarities
        matrix_data = []
        for i, role1 in enumerate(roles):
            row = []
            for j, role2 in enumerate(roles):
                if i == j:
                    row.append(1.0)  # Perfect agreement with self
                else:
                    # Placeholder - would calculate real agreement in full implementation
                    row.append(0.7)  # Moderate agreement with others
            matrix_data.append(row)
        
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Agent Agreement Matrix</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ color: #333366; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Agent Agreement Matrix</h1>
        <div id="heatmap"></div>
    </div>
    
    <script>
        var data = [{{
            z: {json.dumps(matrix_data)},
            x: {json.dumps(roles)},
            y: {json.dumps(roles)},
            type: 'heatmap',
            colorscale: 'Viridis',
            showscale: true
        }}];
        
        var layout = {{
            title: 'Inter-Agent Agreement Scores',
            xaxis: {{ title: 'Agent Role' }},
            yaxis: {{ title: 'Agent Role' }},
            width: 800,
            height: 800
        }};
        
        Plotly.newPlot('heatmap', data, layout);
    </script>
</body>
</html>"""
        
        # Write HTML to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"Generated agreement matrix: {output_path}")
        return output_path
    
    def _generate_html_content(
        self,
        case_study: str,
        case_summary: Dict[str, Any],
        responses_by_role: Dict[str, List[Dict[str, Any]]],
        final_consensus: Dict[str, Any],
        performance: Dict[str, Any]
    ) -> str:
        """
        Generate HTML content for the deliberation report.
        
        Args:
            case_study: Case study text
            case_summary: Case summary dictionary
            responses_by_role: Dictionary of responses grouped by role
            final_consensus: Final consensus dictionary
            performance: Performance metrics dictionary
            
        Returns:
            HTML content as a string
        """
        # Format case study
        case_study_html = case_study.replace("\n", "<br>")
        
        # Format agent responses
        agent_responses_html = ""
        for role, responses in responses_by_role.items():
            agent_responses_html += f'<div class="role-section"><h3>{role}</h3>'
            for i, response in enumerate(responses):
                agent_responses_html += f'<div class="response"><h4>Round {i+1}</h4>'
                agent_responses_html += f'<p>{response.get("response", "").replace("\n", "<br>")}</p>'
                agent_responses_html += f'<p class="confidence">Confidence: {response.get("confidence", 0):.2f}</p>'
                agent_responses_html += '</div>'
            agent_responses_html += '</div>'
        
        # Format final consensus
        final_consensus_html = f'<h3>Summary</h3><p>{final_consensus.get("summary", "").replace("\n", "<br>")}</p>'
        final_consensus_html += f'<h3>Recommendation</h3><p>{final_consensus.get("recommendation", "").replace("\n", "<br>")}</p>'
        final_consensus_html += f'<h3>Confidence</h3><p>{final_consensus.get("confidence", 0):.2f}</p>'
        
        if "key_considerations" in final_consensus and final_consensus["key_considerations"]:
            final_consensus_html += '<h3>Key Considerations</h3><ul>'
            for consideration in final_consensus["key_considerations"]:
                final_consensus_html += f'<li>{consideration}</li>'
            final_consensus_html += '</ul>'
        
        if "ethical_principles" in final_consensus and final_consensus["ethical_principles"]:
            final_consensus_html += '<h3>Ethical Principles</h3><ul>'
            for principle in final_consensus["ethical_principles"]:
                final_consensus_html += f'<li>{principle}</li>'
            final_consensus_html += '</ul>'
        
        # Format performance metrics
        performance_html = '<table>'
        if "response_times" in performance:
            performance_html += f'<tr><td>Average Response Time</td><td>{performance["response_times"].get("average_ms", 0)} ms</td></tr>'
        if "token_usage" in performance:
            performance_html += f'<tr><td>Total Tokens</td><td>{performance["token_usage"].get("total_tokens", 0)}</td></tr>'
            performance_html += f'<tr><td>Total Cost</td><td>${performance["token_usage"].get("total_cost", 0):.4f}</td></tr>'
        performance_html += '</table>'
        
        # Generate timeline data for visualization
        timeline_data = []
        round_number = 1
        for role, responses in responses_by_role.items():
            for i, response in enumerate(responses):
                timeline_data.append({
                    "round": round_number + i,
                    "role": role,
                    "confidence": response.get("confidence", 0.5)
                })
        
        # Full HTML template
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Deliberation Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .section {{
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }}
        .role-section {{
            margin-bottom: 30px;
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
        }}
        .response {{
            margin-left: 20px;
            border-left: 3px solid #3498db;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .confidence {{
            color: #7f8c8d;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        .metrics {{
            display: flex;
            justify-content: space-between;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            width: 30%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .tabs {{
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
        }}
        .tabs button {{
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            font-size: 17px;
        }}
        .tabs button:hover {{
            background-color: #ddd;
        }}
        .tabs button.active {{
            background-color: #3498db;
            color: white;
        }}
        .tabcontent {{
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Ethical Deliberation Report</h1>
        <div class="section">
            <h2>Case Information</h2>
            <p><strong>Title:</strong> {case_summary.get("title", "Ethical Case Study")}</p>
            <p><strong>Start Time:</strong> {case_summary.get("start_time", "")}</p>
            <p><strong>End Time:</strong> {case_summary.get("end_time", "")}</p>
            <p><strong>Total Rounds:</strong> {case_summary.get("total_rounds", 0)}</p>
            <p><strong>Consensus Reached:</strong> {case_summary.get("consensus_reached", False)}</p>
        </div>
        
        <div class="tabs">
            <button class="tablinks active" onclick="openTab(event, 'CaseStudy')">Case Study</button>
            <button class="tablinks" onclick="openTab(event, 'AgentResponses')">Agent Responses</button>
            <button class="tablinks" onclick="openTab(event, 'FinalConsensus')">Final Consensus</button>
            <button class="tablinks" onclick="openTab(event, 'Metrics')">Metrics</button>
            <button class="tablinks" onclick="openTab(event, 'Visualization')">Visualization</button>
        </div>
        
        <div id="CaseStudy" class="tabcontent" style="display: block;">
            <h2>Case Study</h2>
            <p>{case_study_html}</p>
        </div>
        
        <div id="AgentResponses" class="tabcontent">
            <h2>Agent Responses</h2>
            {agent_responses_html}
        </div>
        
        <div id="FinalConsensus" class="tabcontent">
            <h2>Final Consensus</h2>
            {final_consensus_html}
        </div>
        
        <div id="Metrics" class="tabcontent">
            <h2>Performance Metrics</h2>
            <div class="metrics">
                <div class="metric-card">
                    <h3>API Metrics</h3>
                    {performance_html}
                </div>
            </div>
        </div>
        
        <div id="Visualization" class="tabcontent">
            <h2>Deliberation Visualization</h2>
            <div id="timeline"></div>
        </div>
    </div>
    
    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }}
        
        // Initialize timeline visualization
        var timelineData = {json.dumps(timeline_data)};
        
        var traces = [];
        var roles = [...new Set(timelineData.map(item => item.role))];
        
        roles.forEach(role => {{
            var roleData = timelineData.filter(item => item.role === role);
            traces.push({{
                x: roleData.map(item => item.round),
                y: roleData.map(item => item.confidence),
                mode: 'lines+markers',
                name: role,
                line: {{ width: 3 }},
                marker: {{ size: 10 }}
            }});
        }});
        
        var layout = {{
            title: 'Agent Confidence Over Deliberation Rounds',
            xaxis: {{ title: 'Round' }},
            yaxis: {{ title: 'Confidence', range: [0, 1] }},
            hovermode: 'closest'
        }};
        
        Plotly.newPlot('timeline', traces, layout);
    </script>
</body>
</html>"""
        
        return html 