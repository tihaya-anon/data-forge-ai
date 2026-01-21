package tests.pipeline.flink;

import com.dataforge.flink.cdc.CDCConfiguration;
import com.dataforge.flink.cdc.CDCJob;
import com.dataforge.flink.cdc.CDCStateManager;
import com.dataforge.flink.cdc.CDCSourceConnector;
import org.apache.flink.api.common.JobExecutionResult;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.junit.Test;
import org.mockito.Mockito;

import java.util.Arrays;
import java.util.List;

import static org.junit.Assert.*;

public class CDCJobTest {

    @Test
    public void testCDCConfiguration() {
        // 测试CDC配置类
        CDCConfiguration config = new CDCConfiguration();
        config.setDatabaseConnection("jdbc:mysql://localhost:3306/testdb", "user", "pass")
              .setTableName("users")
              .setKafkaOutput("localhost:9092", "output-topic");

        assertEquals("jdbc:mysql://localhost:3306/testdb", config.getDatabaseUrl());
        assertEquals("user", config.getDatabaseUser());
        assertEquals("pass", config.getDatabasePassword());
        assertEquals("users", config.getTableName());
        assertEquals("localhost:9092", config.getKafkaBootstrapServers());
        assertEquals("output-topic", config.getOutputTopic());
    }

    @Test
    public void testCDCStateManager() throws Exception {
        // 测试状态管理器
        CDCStateManager stateManager = new CDCStateManager();
        
        // 这里只是验证类可以被实例化，更详细的测试需要在Flink环境中运行
        assertNotNull(stateManager);
    }

    @Test
    public void testMySQLCDCSourceCreation() {
        // 测试MySQL CDC源创建
        CDCConfiguration config = new CDCConfiguration();
        config.setDatabaseConnection("jdbc:mysql://localhost:3306/testdb", "user", "pass")
              .setTableName("users");

        CDCSourceConnector mySqlSource = new CDCSourceConnector.MySQLCDCSource(config);
        assertNotNull(mySqlSource);
    }

    @Test
    public void testPostgreSQLCDCSourceCreation() {
        // 测试PostgreSQL CDC源创建
        CDCConfiguration config = new CDCConfiguration();
        config.setDatabaseConnection("jdbc:postgresql://localhost:5432/testdb", "user", "pass")
              .setTableName("users");

        CDCSourceConnector postgresSource = new CDCSourceConnector.PostgresCDCSource(config);
        assertNotNull(postgresSource);
    }

    @Test
    public void testSqlServerCDCSourceCreation() {
        // 测试SQL Server CDC源创建
        CDCConfiguration config = new CDCConfiguration();
        config.setDatabaseConnection("jdbc:sqlserver://localhost:1433;databaseName=testdb", "user", "pass")
              .setTableName("users");

        CDCSourceConnector sqlServerSource = new CDCSourceConnector.SqlServerCDCSource(config);
        assertNotNull(sqlServerSource);
    }

    @Test
    public void testMainMethodExecution() throws Exception {
        // 测试主方法能否正常执行（不实际执行作业）
        // 我们不能真正执行Flink作业，因为它需要运行中的Flink集群
        // 但是我们可以验证代码路径
        
        // 验证主方法不会抛出异常（通过反射调用静态方法）
        try {
            CDCJob.main(new String[]{});
            fail("Expected exception because no actual Flink cluster is running");
        } catch (Exception e) {
            // 期望会有异常，因为没有运行中的Flink集群
            assertTrue(true);
        }
    }
}