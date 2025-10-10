#!/usr/bin/env python3
"""
RaceCast System Design Diagram
Generates a comprehensive system architecture diagram for the RaceCast F1 Analytics Platform
"""

import graphviz
from pathlib import Path

def create_racecast_system_diagram():
    """Create comprehensive system design diagram for RaceCast"""
    
    # Create directed graph
    dot = graphviz.Digraph(comment='RaceCast System Architecture')
    dot.attr(rankdir='TB', size='16,20', bgcolor='white', dpi='300')
    dot.attr('node', shape='box', style='filled', fontname='Arial', fontsize='12', width='2.5', height='1.2')
    dot.attr('edge', fontname='Arial', fontsize='11')
    
    # Define colors
    colors = {
        'frontend': '#3B82F6',      # Blue
        'backend': '#10B981',       # Green  
        'database': '#F59E0B',      # Orange
        'ml': '#8B5CF6',           # Purple
        'external': '#EF4444',     # Red
        'infrastructure': '#6B7280', # Gray
        'data': '#06B6D4'          # Cyan
    }
    
    # Frontend Layer
    with dot.subgraph(name='cluster_frontend') as c:
        c.attr(style='filled', color='lightblue', label='Frontend Layer (Vercel)')
        c.node('nextjs', 'Next.js 15.2.4\nReact 19', fillcolor=colors['frontend'])
        c.node('tailwind', 'Tailwind CSS\nshadcn/ui', fillcolor=colors['frontend'])
        c.node('zustand', 'Zustand\nState Management', fillcolor=colors['frontend'])
        c.node('react_query', 'TanStack Query\nData Fetching', fillcolor=colors['frontend'])
        c.node('recharts', 'Recharts\nData Visualization', fillcolor=colors['frontend'])
        c.node('vercel_cron', 'Vercel Cron Jobs\nAutomation', fillcolor=colors['infrastructure'])
    
    # Backend Layer
    with dot.subgraph(name='cluster_backend') as c:
        c.attr(style='filled', color='lightgreen', label='Backend Layer (Render)')
        c.node('fastapi', 'FastAPI\nPython Backend', fillcolor=colors['backend'])
        c.node('uvicorn', 'Uvicorn\nASGI Server', fillcolor=colors['backend'])
        c.node('sqlalchemy', 'SQLAlchemy\nORM', fillcolor=colors['backend'])
        c.node('pydantic', 'Pydantic\nData Validation', fillcolor=colors['backend'])
        c.node('cors', 'CORS\nMiddleware', fillcolor=colors['backend'])
        c.node('auth', 'API Key\nAuthentication', fillcolor=colors['backend'])
    
    # ML Layer
    with dot.subgraph(name='cluster_ml') as c:
        c.attr(style='filled', color='plum', label='ML Layer')
        c.node('xgboost', 'XGBoost\nRanker Model', fillcolor=colors['ml'])
        c.node('feature_eng', 'Feature Engineering\n110+ Features', fillcolor=colors['ml'])
        c.node('model_pkl', 'Persisted Model\n(.pkl file)', fillcolor=colors['ml'])
        c.node('predictor', 'RankerPredictor\nService', fillcolor=colors['ml'])
        c.node('label_enc', 'Label Encoders\nCategorical Data', fillcolor=colors['ml'])
    
    # Database Layer
    with dot.subgraph(name='cluster_database') as c:
        c.attr(style='filled', color='lightyellow', label='Database Layer (Neon)')
        c.node('postgres', 'PostgreSQL\nServerless', fillcolor=colors['database'])
        c.node('predictions', 'Predictions Table\nRace Results', fillcolor=colors['database'])
        c.node('results', 'Results Table\nActual Results', fillcolor=colors['database'])
        c.node('races', 'Races Table\nRace Information', fillcolor=colors['database'])
    
    # Data Sources
    with dot.subgraph(name='cluster_data') as c:
        c.attr(style='filled', color='lightcyan', label='Data Sources')
        c.node('ergast', 'Ergast F1 API\nHistorical Data', fillcolor=colors['external'])
        c.node('fastf1', 'FastF1\nTelemetry Data', fillcolor=colors['external'])
        c.node('enhanced_dataset', 'Enhanced Dataset\n3,318 Records', fillcolor=colors['data'])
        c.node('cache', 'FastF1 Cache\nLocal Storage', fillcolor=colors['data'])
    
    # Infrastructure
    with dot.subgraph(name='cluster_infra') as c:
        c.attr(style='filled', color='lightgray', label='Infrastructure')
        c.node('docker', 'Docker\nContainerization', fillcolor=colors['infrastructure'])
        c.node('render', 'Render\nBackend Hosting', fillcolor=colors['infrastructure'])
        c.node('vercel', 'Vercel\nFrontend Hosting', fillcolor=colors['infrastructure'])
        c.node('neon', 'Neon\nDatabase Hosting', fillcolor=colors['infrastructure'])
    
    # API Endpoints
    with dot.subgraph(name='cluster_apis') as c:
        c.attr(style='filled', color='lightcoral', label='API Endpoints')
        c.node('predict_api', '/predict\nRace Predictions', fillcolor=colors['backend'])
        c.node('results_api', '/update_results\nResult Updates', fillcolor=colors['backend'])
        c.node('health_api', '/healthz\nHealth Check', fillcolor=colors['backend'])
        c.node('predictions_api', '/predictions\nGet Predictions', fillcolor=colors['backend'])
    
    # Frontend Components
    with dot.subgraph(name='cluster_components') as c:
        c.attr(style='filled', color='lightsteelblue', label='Frontend Components')
        c.node('race_pred', 'Race Prediction\nComponent', fillcolor=colors['frontend'])
        c.node('driver_perf', 'Driver Performance\nComponent', fillcolor=colors['frontend'])
        c.node('constructor_perf', 'Constructor Performance\nComponent', fillcolor=colors['frontend'])
        c.node('era_analysis', 'Era Analysis\nComponent', fillcolor=colors['frontend'])
        c.node('personality', 'Driver Personality\nComponent', fillcolor=colors['frontend'])
        c.node('trends', 'Winning Trends\nComponent', fillcolor=colors['frontend'])
    
    # Data Flow Connections
    # Frontend to Backend
    dot.edge('nextjs', 'fastapi', label='API Calls', color='blue')
    dot.edge('react_query', 'fastapi', label='Data Fetching', color='blue')
    dot.edge('vercel_cron', 'fastapi', label='Automated Updates', color='blue')
    
    # Backend to ML (Inference - Stateless)
    dot.edge('fastapi', 'predictor', label='API Call to model.pkl service', color='green')
    dot.edge('predictor', 'model_pkl', label='Load Model', color='purple')
    dot.edge('model_pkl', 'xgboost', label='Model Inference', color='purple')
    
    # Backend to Database
    dot.edge('fastapi', 'postgres', label='Database Operations', color='orange')
    dot.edge('sqlalchemy', 'postgres', label='ORM Queries', color='orange')
    dot.edge('predictions', 'postgres', label='Store Predictions', color='orange')
    dot.edge('results', 'postgres', label='Store Results', color='orange')
    
    # Training Data Flow (One-time)
    dot.edge('ergast', 'enhanced_dataset', label='Historical Data', color='red', style='dashed')
    dot.edge('fastf1', 'enhanced_dataset', label='Telemetry Data', color='red', style='dashed')
    dot.edge('enhanced_dataset', 'feature_eng', label='Training Data', color='cyan', style='dashed')
    dot.edge('feature_eng', 'xgboost', label='Model Training', color='purple', style='dashed')
    dot.edge('xgboost', 'model_pkl', label='Save Model', color='purple', style='dashed')
    dot.edge('cache', 'fastf1', label='Cached Data', color='cyan')
    
    # API Endpoints
    dot.edge('fastapi', 'predict_api', label='Serves', color='green')
    dot.edge('fastapi', 'results_api', label='Serves', color='green')
    dot.edge('fastapi', 'health_api', label='Serves', color='green')
    dot.edge('fastapi', 'predictions_api', label='Serves', color='green')
    
    # Frontend Components
    dot.edge('nextjs', 'race_pred', label='Renders', color='blue')
    dot.edge('nextjs', 'driver_perf', label='Renders', color='blue')
    dot.edge('nextjs', 'constructor_perf', label='Renders', color='blue')
    dot.edge('nextjs', 'era_analysis', label='Renders', color='blue')
    dot.edge('nextjs', 'personality', label='Renders', color='blue')
    dot.edge('nextjs', 'trends', label='Renders', color='blue')
    
    # Infrastructure
    dot.edge('docker', 'render', label='Deployed on', color='gray')
    dot.edge('fastapi', 'docker', label='Containerized', color='gray')
    dot.edge('nextjs', 'vercel', label='Deployed on', color='gray')
    dot.edge('postgres', 'neon', label='Hosted on', color='gray')
    
    # Data Flow Labels
    dot.edge('enhanced_dataset', 'xgboost', label='Training', color='purple', style='dashed')
    dot.edge('ergast', 'fastapi', label='Live Data', color='red', style='dashed')
    
    # Legend (Compact)
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(style='filled', color='lightgray', label='Legend', fontsize='8')
        c.attr(rank='same')
        c.node('legend_frontend', 'Frontend', fillcolor=colors['frontend'], fontsize='7', width='1.2', height='0.6')
        c.node('legend_backend', 'Backend', fillcolor=colors['backend'], fontsize='7', width='1.2', height='0.6')
        c.node('legend_ml', 'ML', fillcolor=colors['ml'], fontsize='7', width='1.2', height='0.6')
        c.node('legend_database', 'Database', fillcolor=colors['database'], fontsize='7', width='1.2', height='0.6')
        c.node('legend_external', 'External', fillcolor=colors['external'], fontsize='7', width='1.2', height='0.6')
        c.node('legend_infrastructure', 'Infra', fillcolor=colors['infrastructure'], fontsize='7', width='1.2', height='0.6')
    
    return dot

def create_data_flow_diagram():
    """Create detailed data flow diagram"""
    
    dot = graphviz.Digraph(comment='RaceCast Data Flow')
    dot.attr(rankdir='LR', size='20,12', bgcolor='white', dpi='300')
    dot.attr('node', shape='box', style='filled', fontname='Arial', fontsize='12', width='2.5', height='1.2')
    
    # Data sources
    dot.node('ergast_api', 'Ergast F1 API\nHistorical Data', fillcolor='#EF4444')
    dot.node('fastf1_api', 'FastF1\nTelemetry Data', fillcolor='#EF4444')
    
    # Data processing (Training Phase)
    dot.node('data_collector', 'Data Collectors\nErgastCollector\nFastF1Collector', fillcolor='#06B6D4')
    dot.node('feature_engineer', 'Feature Engineering\n110+ Features\nEnhanced Dataset', fillcolor='#8B5CF6')
    dot.node('model_training', 'XGBoost Training\n3,318 Records\nRanker Model', fillcolor='#8B5CF6')
    dot.node('model_file', 'Model File\n(.pkl)', fillcolor='#8B5CF6')
    
    # Model serving (Inference Phase)
    dot.node('model_serving', 'Model Serving\nRankerPredictor\nStateless Inference', fillcolor='#10B981')
    dot.node('api_endpoints', 'API Endpoints\n/predict\n/update_results', fillcolor='#10B981')
    
    # Storage
    dot.node('database', 'Neon PostgreSQL\nPredictions\nResults\nRaces', fillcolor='#F59E0B')
    dot.node('cache', 'FastF1 Cache\nLocal Storage', fillcolor='#6B7280')
    
    # Frontend
    dot.node('frontend', 'Next.js Frontend\nDashboard\nVisualizations', fillcolor='#3B82F6')
    
    # Training Data Flow (One-time, dashed)
    dot.edge('ergast_api', 'data_collector', label='Historical Data', style='dashed')
    dot.edge('fastf1_api', 'data_collector', label='Telemetry Data', style='dashed')
    dot.edge('data_collector', 'feature_engineer', label='Raw Data', style='dashed')
    dot.edge('feature_engineer', 'model_training', label='Enhanced Dataset', style='dashed')
    dot.edge('model_training', 'model_file', label='Save Model', style='dashed')
    
    # Inference Data Flow (Real-time, solid)
    dot.edge('model_file', 'model_serving', label='Load Model')
    dot.edge('model_serving', 'api_endpoints', label='API Call to model.pkl service')
    dot.edge('api_endpoints', 'database', label='Store Results')
    dot.edge('api_endpoints', 'frontend', label='API Responses')
    dot.edge('fastf1_api', 'cache', label='Cache Data')
    dot.edge('cache', 'data_collector', label='Cached Data')
    
    # Legend (Compact)
    with dot.subgraph(name='cluster_legend') as c:
        c.attr(style='filled', color='lightgray', label='Legend', fontsize='8')
        c.attr(rank='same')
        c.node('legend_training', 'Training', fillcolor='white', fontsize='7', style='dashed', width='1.2', height='0.6')
        c.node('legend_inference', 'Inference', fillcolor='white', fontsize='7', style='solid', width='1.2', height='0.6')
        c.node('legend_data', 'Data', fillcolor='#EF4444', fontsize='7', width='1.2', height='0.6')
        c.node('legend_processing', 'Process', fillcolor='#06B6D4', fontsize='7', width='1.2', height='0.6')
        c.node('legend_ml', 'ML', fillcolor='#8B5CF6', fontsize='7', width='1.2', height='0.6')
        c.node('legend_api', 'API', fillcolor='#10B981', fontsize='7', width='1.2', height='0.6')
        c.node('legend_storage', 'Storage', fillcolor='#F59E0B', fontsize='7', width='1.2', height='0.6')
        c.node('legend_frontend', 'Frontend', fillcolor='#3B82F6', fontsize='7', width='1.2', height='0.6')
    
    return dot

def main():
    """Generate system design diagrams"""
    
    print("🏎️ Generating RaceCast System Design Diagrams...")
    
    # Create main system diagram
    system_diagram = create_racecast_system_diagram()
    system_diagram.render('racecast_system_architecture', format='png', cleanup=True)
    system_diagram.render('racecast_system_architecture', format='svg', cleanup=True)
    print("✅ System Architecture diagram generated: racecast_system_architecture.png/svg")
    
    # Create data flow diagram
    data_flow_diagram = create_data_flow_diagram()
    data_flow_diagram.render('racecast_data_flow', format='png', cleanup=True)
    data_flow_diagram.render('racecast_data_flow', format='svg', cleanup=True)
    print("✅ Data Flow diagram generated: racecast_data_flow.png/svg")
    
    print("\n🎯 Diagrams created successfully!")
    print("📁 Files generated:")
    print("   - racecast_system_architecture.png")
    print("   - racecast_system_architecture.svg")
    print("   - racecast_data_flow.png")
    print("   - racecast_data_flow.svg")

if __name__ == "__main__":
    main()
