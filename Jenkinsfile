// Jenkinsfile for ACEest Fitness & Gym Management Application
// Declarative Pipeline with SonarQube, Docker Hub, and Kubernetes

pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO     = "your-dockerhub-username/aceest-fitness-gym"
        DOCKER_HUB_CREDS    = credentials('dockerhub-credentials')
        SONAR_HOST_URL      = "http://localhost:9000"
        SONAR_PROJECT_KEY   = "aceest-fitness-gym"
        KUBECONFIG_PATH     = "/home/jenkins/.kube/config"
        APP_VERSION         = "1.0.${BUILD_NUMBER}"
        BLUE_LABEL          = "blue"
        GREEN_LABEL         = "green"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }

    stages {

        // ─────────────────────────────────────────────
        // STAGE 1: Source Checkout
        // ─────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '========== Checking out source code =========='
                checkout scm
                sh 'git log --oneline -5'
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 2: Python Environment Setup
        // ─────────────────────────────────────────────
        stage('Setup Environment') {
            steps {
                echo '========== Setting up Python virtual environment =========='
                sh '''
                    python3 --version
                    pip3 --version
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip setuptools wheel
                '''
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 3: Install Dependencies
        // ─────────────────────────────────────────────
        stage('Install Dependencies') {
            steps {
                echo '========== Installing project dependencies =========='
                sh '''
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pip install flake8 pytest pytest-cov pytest-html
                '''
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 4: Code Quality – Lint
        // ─────────────────────────────────────────────
        stage('Code Quality - Lint') {
            steps {
                echo '========== Running flake8 linting =========='
                sh '''
                    . venv/bin/activate
                    flake8 app.py test_app.py \
                        --count \
                        --max-line-length=127 \
                        --max-complexity=10 \
                        --statistics \
                        --format=default \
                        || true
                '''
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 5: Syntax Check
        // ─────────────────────────────────────────────
        stage('Syntax Check') {
            steps {
                echo '========== Checking Python syntax =========='
                sh '''
                    . venv/bin/activate
                    python3 -m py_compile app.py test_app.py
                    echo "Syntax check passed"
                '''
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 6: Unit Tests with Pytest
        // ─────────────────────────────────────────────
        stage('Unit Tests') {
            steps {
                echo '========== Running Pytest unit tests =========='
                sh '''
                    . venv/bin/activate
                    mkdir -p xmlreport
                    pytest test_app.py \
                        -v \
                        --tb=short \
                        --cov=app \
                        --cov-report=xml:coverage.xml \
                        --cov-report=html:htmlcov \
                        --junitxml=xmlreport/test-results.xml \
                        --html=xmlreport/test-report.html \
                        --self-contained-html
                '''
            }
            post {
                always {
                    junit testResults: 'xmlreport/test-results.xml', skipPublishingChecks: true
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

        // ─────────────────────────────────────────────
        // STAGE 7: SonarQube Static Analysis
        // ─────────────────────────────────────────────
        stage('SonarQube Analysis') {
            steps {
                echo '========== Running SonarQube analysis =========='
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.projectName="ACEest Fitness Gym" \
                            -Dsonar.projectVersion=${APP_VERSION} \
                            -Dsonar.sources=. \
                            -Dsonar.inclusions=app.py \
                            -Dsonar.tests=. \
                            -Dsonar.test.inclusions=test_app.py \
                            -Dsonar.python.coverage.reportPaths=coverage.xml \
                            -Dsonar.python.xunit.reportPath=xmlreport/test-results.xml \
                            -Dsonar.host.url=${SONAR_HOST_URL}
                    '''
                }
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 8: SonarQube Quality Gate
        // ─────────────────────────────────────────────
        stage('Quality Gate') {
            steps {
                echo '========== Waiting for SonarQube Quality Gate =========='
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 9: Build Docker Image
        // ─────────────────────────────────────────────
        stage('Build Docker Image') {
            steps {
                echo '========== Building Docker image =========='
                sh """
                    docker build -t ${DOCKER_HUB_REPO}:latest .
                    docker build -t ${DOCKER_HUB_REPO}:${APP_VERSION} .
                    docker images | grep ${DOCKER_HUB_REPO}
                """
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 10: Test Docker Container
        // ─────────────────────────────────────────────
        stage('Test Docker Container') {
            steps {
                echo '========== Running tests inside Docker container =========='
                sh """
                    docker run --rm ${DOCKER_HUB_REPO}:latest \
                        pytest test_app.py -v --tb=short

                    CONTAINER_ID=\$(docker run -d -p 5001:5000 ${DOCKER_HUB_REPO}:latest)
                    sleep 5
                    curl -f http://localhost:5001/health || (docker stop \$CONTAINER_ID && exit 1)
                    docker stop \$CONTAINER_ID
                """
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 11: Push to Docker Hub
        // ─────────────────────────────────────────────
        stage('Push to Docker Hub') {
            steps {
                echo '========== Pushing image to Docker Hub =========='
                sh """
                    echo \${DOCKER_HUB_CREDS_PSW} | docker login -u \${DOCKER_HUB_CREDS_USR} --password-stdin
                    docker push ${DOCKER_HUB_REPO}:latest
                    docker push ${DOCKER_HUB_REPO}:${APP_VERSION}
                    docker logout
                """
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 12: Rolling Update Deployment
        // ─────────────────────────────────────────────
        stage('Deploy - Rolling Update') {
            when { branch 'main' }
            steps {
                echo '========== Deploying with Rolling Update strategy =========='
                sh """
                    export KUBECONFIG=${KUBECONFIG_PATH}
                    kubectl apply -f k8s/rolling-update/deployment.yaml
                    kubectl set image deployment/aceest-rolling \
                        aceest-app=${DOCKER_HUB_REPO}:${APP_VERSION} \
                        --record || true
                    kubectl rollout status deployment/aceest-rolling --timeout=120s
                """
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 13: Blue-Green Deployment
        // ─────────────────────────────────────────────
        stage('Deploy - Blue-Green') {
            when { branch 'main' }
            steps {
                echo '========== Deploying with Blue-Green strategy =========='
                sh """
                    export KUBECONFIG=${KUBECONFIG_PATH}
                    # Deploy green version
                    sed -i 's|IMAGE_PLACEHOLDER|${DOCKER_HUB_REPO}:${APP_VERSION}|g' k8s/blue-green/green-deployment.yaml
                    kubectl apply -f k8s/blue-green/green-deployment.yaml
                    kubectl rollout status deployment/aceest-green --timeout=120s

                    # Switch traffic to green
                    kubectl apply -f k8s/blue-green/service.yaml
                    kubectl patch service aceest-service -p '{"spec":{"selector":{"slot":"green"}}}'

                    echo "Blue-Green: traffic switched to GREEN (v${APP_VERSION})"
                """
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 14: Canary Release
        // ─────────────────────────────────────────────
        stage('Deploy - Canary') {
            when { branch 'main' }
            steps {
                echo '========== Deploying with Canary strategy (10% traffic) =========='
                sh """
                    export KUBECONFIG=${KUBECONFIG_PATH}
                    sed -i 's|IMAGE_PLACEHOLDER|${DOCKER_HUB_REPO}:${APP_VERSION}|g' k8s/canary/canary-deployment.yaml
                    kubectl apply -f k8s/canary/canary-deployment.yaml
                    kubectl rollout status deployment/aceest-canary --timeout=120s
                    echo "Canary deployment live — 10% of traffic routed to v${APP_VERSION}"
                """
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 15: Shadow Deployment
        // ─────────────────────────────────────────────
        stage('Deploy - Shadow') {
            when { branch 'main' }
            steps {
                echo '========== Deploying Shadow instance (no live traffic) =========='
                sh """
                    export KUBECONFIG=${KUBECONFIG_PATH}
                    sed -i 's|IMAGE_PLACEHOLDER|${DOCKER_HUB_REPO}:${APP_VERSION}|g' k8s/shadow/shadow-deployment.yaml
                    kubectl apply -f k8s/shadow/shadow-deployment.yaml
                    kubectl rollout status deployment/aceest-shadow --timeout=120s
                    echo "Shadow deployment running — mirroring production traffic for testing"
                """
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 16: A/B Testing Deployment
        // ─────────────────────────────────────────────
        stage('Deploy - A/B Testing') {
            when { branch 'main' }
            steps {
                echo '========== Deploying A/B Testing variants =========='
                sh """
                    export KUBECONFIG=${KUBECONFIG_PATH}
                    kubectl apply -f k8s/ab-testing/version-a-deployment.yaml
                    kubectl apply -f k8s/ab-testing/version-b-deployment.yaml
                    kubectl apply -f k8s/ab-testing/service.yaml
                    kubectl rollout status deployment/aceest-version-a --timeout=120s
                    kubectl rollout status deployment/aceest-version-b --timeout=120s
                    echo "A/B Testing: Version A (stable) and Version B (new) both live"
                """
            }
        }

        // ─────────────────────────────────────────────
        // STAGE 17: Archive Artifacts
        // ─────────────────────────────────────────────
        stage('Archive Artifacts') {
            steps {
                echo '========== Archiving build artifacts =========='
                archiveArtifacts artifacts: '''
                    app.py,
                    test_app.py,
                    requirements.txt,
                    Dockerfile,
                    docker-compose.yml,
                    coverage.xml,
                    xmlreport/**,
                    sonar-project.properties,
                    k8s/**
                ''', allowEmptyArchive: true
            }
        }
    }

    post {
        always {
            echo '========== Cleaning up workspace =========='
            sh '''
                docker rmi $(docker images -q --filter "dangling=true") || true
                rm -rf venv || true
            '''
        }
        success {
            echo "========== Build #${BUILD_NUMBER} SUCCESSFUL — v${APP_VERSION} =========="
        }
        failure {
            echo "========== Build #${BUILD_NUMBER} FAILED — check logs above =========="
        }
        unstable {
            echo "========== Build #${BUILD_NUMBER} UNSTABLE — review warnings =========="
        }
    }
}
