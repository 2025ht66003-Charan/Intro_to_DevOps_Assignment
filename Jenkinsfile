// Jenkinsfile for Fitness & Gym Management Application
// Declarative Pipeline

pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '========== Checking out code =========='
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo '========== Setting up Python environment =========='
                sh '''
                    python --version
                    pip --version
                    python -m venv venv || python3 -m venv venv
                    . venv/bin/activate || source venv/bin/activate
                    pip install --upgrade pip setuptools wheel
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '========== Installing project dependencies =========='
                sh '''
                    . venv/bin/activate || source venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Code Quality - Lint') {
            steps {
                echo '========== Running code linting =========='
                sh '''
                    . venv/bin/activate || source venv/bin/activate
                    pip install flake8
                    flake8 app.py test_app.py --count --statistics || true
                '''
            }
        }
        
        stage('Syntax Check') {
            steps {
                echo '========== Checking Python syntax =========='
                sh '''
                    . venv/bin/activate || source venv/bin/activate
                    python -m py_compile app.py test_app.py
                '''
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo '========== Running unit tests =========='
                sh '''
                    . venv/bin/activate || source venv/bin/activate
                    pip install pytest pytest-cov
                    pytest test_app.py -v --tb=short --cov=app --cov-report=xml --cov-report=html
                    
                '''
            }
            post {
                always {
                    junit testResults: 'xmlreport/*.xml', skipPublishingChecks: true
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Code Coverage Report'
                    ])
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '========== Building Docker image =========='
                sh '''
                    docker build -t fitness-gym-app:latest .
                    docker build -t fitness-gym-app:${BUILD_NUMBER} .
                '''
            }
        }
        
        stage('Test Docker Container') {
            steps {
                echo '========== Testing Docker container =========='
                sh '''
                    # Run tests in Docker container
                    docker run --rm fitness-gym-app:latest pytest test_app.py -v
                    
                    # Start container and test health check
                    CONTAINER_ID=$(docker run -d -p 5000:5000 fitness-gym-app:latest)
                    sleep 5
                    
                    # Test health endpoint
                    curl -f http://localhost:5000/health || exit 1
                    
                    # Stop container
                    docker stop $CONTAINER_ID || true
                '''
            }
        }
        
        stage('Quality Gate') {
            steps {
                echo '========== Running Quality Gate =========='
                sh '''
                    . venv/bin/activate || source venv/bin/activate
                    
                    # Check if tests passed
                    if [ $? -eq 0 ]; then
                        echo "✓ Quality Gate PASSED"
                    else
                        echo "✗ Quality Gate FAILED"
                        exit 1
                    fi
                '''
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                echo '========== Archiving artifacts =========='
                archiveArtifacts artifacts: '*.py, requirements.txt, Dockerfile, docker-compose.yml, .github/**', 
                                  allowEmptyArchive: true
            }
        }
    }
    
    post {
        always {
            echo '========== Cleaning up =========='
            sh '''
                # Clean up Docker containers
                docker ps -a -q | xargs -r docker rm || true
                
                # Remove venv
                rm -rf venv || true
            '''
        }
        success {
            echo '========== Build Successful =========='
            echo 'The application built successfully and all tests passed!'
        }
        failure {
            echo '========== Build Failed =========='
            echo 'The build failed. Check the logs above for details.'
        }
        unstable {
            echo '========== Build Unstable =========='
            echo 'The build is unstable. Review the warnings and issues.'
        }
    }
}
