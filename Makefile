REDSHIFT_CLUSTER_IDENTIFIER = pgbedrock-redshift
REDSHIFT_DB = test_db
REDSHIFT_USER = test_user
REDSHIFT_PASSWORD = test_Pa55w0rd
REDSHIFT_PORT = 5439

start_redshift:
		@echo "Starting redshift cluster"
		@aws redshift create-cluster \
		  --db-name ${REDSHIFT_DB} \
		  --cluster-identifier ${REDSHIFT_CLUSTER_IDENTIFIER} \
		  --cluster-type single-node \
		  --node-type dc2.large \
		  --master-username $(REDSHIFT_USER) \
		  --master-user-password ${REDSHIFT_PASSWORD} \
		  --port ${REDSHIFT_PORT} \
		  --publicly-accessible
		@echo "Sleeping while redshift cluster starts";
		@aws redshift wait cluster-available \
		  --cluster-identifier ${REDSHIFT_CLUSTER_IDENTIFIER};
		@echo "Redshift cluster started";


delete_redshift:
		@echo "Deleting redshift cluster";
		@aws redshift delete-cluster \
		  --cluster-identifier ${REDSHIFT_CLUSTER_IDENTIFIER} \
		  --skip-final-cluster-snapshot
		@echo "Sleeping while redshift cluster deletes";
		@aws redshift wait cluster-deleted \
		  --cluster-identifier ${REDSHIFT_CLUSTER_IDENTIFIER};
		@echo "Redshift cluster deleted"


check_redshift_clusters:
		@echo "Checking redshift cluster"
		@aws redshift describe-clusters \
		  --cluster-identifier ${REDSHIFT_CLUSTER_IDENTIFIER} 
			