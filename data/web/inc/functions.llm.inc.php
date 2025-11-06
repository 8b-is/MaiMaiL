<?php
/**
 * LLM Email Processing Functions
 * Provides API for LLM-powered email analysis features
 */

function llm($action, $data = null) {
  global $pdo;
  global $lang;

  switch ($action) {
    case 'analyze':
      /**
       * Trigger email analysis
       * Required: mailbox, email_id
       * Optional: force
       */
      if (!isset($data['mailbox']) || !isset($data['email_id'])) {
        $_SESSION['return'][] = array(
          'type' => 'danger',
          'log' => array(__FUNCTION__, $action),
          'msg' => 'Missing required parameters: mailbox, email_id'
        );
        return false;
      }

      try {
        // Call LLM processor service
        $llm_processor_url = 'http://llm-processor-mailcow:8080/analyze';
        $post_data = json_encode(array(
          'mailbox' => $data['mailbox'],
          'email_id' => $data['email_id'],
          'force' => isset($data['force']) ? (bool)$data['force'] : false
        ));

        $ch = curl_init($llm_processor_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
          'Content-Type: application/json',
          'Content-Length: ' . strlen($post_data)
        ));
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);

        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($http_code == 200) {
          $result = json_decode($response, true);
          $_SESSION['return'][] = array(
            'type' => 'success',
            'log' => array(__FUNCTION__, $action),
            'msg' => 'Email analysis completed successfully'
          );
          return $result;
        } else {
          $_SESSION['return'][] = array(
            'type' => 'danger',
            'log' => array(__FUNCTION__, $action),
            'msg' => 'LLM processor returned error: ' . $http_code
          );
          return false;
        }
      } catch (Exception $e) {
        $_SESSION['return'][] = array(
          'type' => 'danger',
          'log' => array(__FUNCTION__, $action, $e->getMessage()),
          'msg' => 'Failed to connect to LLM processor'
        );
        return false;
      }
    break;

    case 'get':
      /**
       * Get LLM analysis results
       * Supports: analysis, stats, config, preferences
       */
      $category = isset($data['category']) ? $data['category'] : 'analysis';

      switch ($category) {
        case 'analysis':
          // Get analysis for specific email or mailbox
          if (isset($data['email_id']) && isset($data['mailbox'])) {
            // Get specific email analysis
            $stmt = $pdo->prepare("SELECT * FROM `llm_email_analysis`
                                  WHERE `mailbox` = :mailbox AND `email_id` = :email_id");
            $stmt->execute(array(':mailbox' => $data['mailbox'], ':email_id' => $data['email_id']));
            return $stmt->fetch(PDO::FETCH_ASSOC);
          } elseif (isset($data['mailbox'])) {
            // Get all analyses for mailbox
            $limit = isset($data['limit']) ? intval($data['limit']) : 50;
            $offset = isset($data['offset']) ? intval($data['offset']) : 0;

            $stmt = $pdo->prepare("SELECT * FROM `llm_email_analysis`
                                  WHERE `mailbox` = :mailbox
                                  ORDER BY `analyzed_at` DESC
                                  LIMIT :limit OFFSET :offset");
            $stmt->bindParam(':mailbox', $data['mailbox']);
            $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
            $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
            $stmt->execute();
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
          } else {
            // Get recent analyses
            $limit = isset($data['limit']) ? intval($data['limit']) : 100;
            $stmt = $pdo->prepare("SELECT * FROM `llm_email_analysis`
                                  ORDER BY `analyzed_at` DESC
                                  LIMIT :limit");
            $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
            $stmt->execute();
            return $stmt->fetchAll(PDO::FETCH_ASSOC);
          }
        break;

        case 'stats':
          // Get processing statistics
          try {
            $llm_processor_url = 'http://llm-processor-mailcow:8080/stats';
            $ch = curl_init($llm_processor_url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, 10);
            $response = curl_exec($ch);
            $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);

            if ($http_code == 200) {
              return json_decode($response, true);
            }
          } catch (Exception $e) {
            return array('error' => 'Failed to fetch stats');
          }
        break;

        case 'config':
          // Get LLM configuration
          $stmt = $pdo->query("SELECT * FROM `llm_config`");
          $configs = $stmt->fetchAll(PDO::FETCH_ASSOC);
          $result = array();
          foreach ($configs as $config) {
            $result[$config['config_key']] = $config['config_value'];
          }
          return $result;
        break;

        case 'preferences':
          // Get user preferences
          if (!isset($data['username'])) {
            return array('error' => 'Username required');
          }
          $stmt = $pdo->prepare("SELECT * FROM `llm_user_preferences` WHERE `username` = :username");
          $stmt->execute(array(':username' => $data['username']));
          return $stmt->fetch(PDO::FETCH_ASSOC);
        break;

        case 'health':
          // Get LLM service health
          try {
            $llm_processor_url = 'http://llm-processor-mailcow:8080/health';
            $ch = curl_init($llm_processor_url);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_TIMEOUT, 5);
            $response = curl_exec($ch);
            $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);

            if ($http_code == 200) {
              return json_decode($response, true);
            } else {
              return array('status' => 'unhealthy', 'error' => 'Service unavailable');
            }
          } catch (Exception $e) {
            return array('status' => 'error', 'message' => $e->getMessage());
          }
        break;
      }
    break;

    case 'edit':
      /**
       * Edit LLM configuration or preferences
       */
      if (!isset($data['category'])) {
        $_SESSION['return'][] = array(
          'type' => 'danger',
          'log' => array(__FUNCTION__, $action),
          'msg' => 'Category required'
        );
        return false;
      }

      switch ($data['category']) {
        case 'config':
          // Update configuration
          foreach ($data['items'] as $key => $value) {
            $stmt = $pdo->prepare("INSERT INTO `llm_config` (`config_key`, `config_value`)
                                  VALUES (:key, :value)
                                  ON DUPLICATE KEY UPDATE `config_value` = :value");
            $stmt->execute(array(':key' => $key, ':value' => $value));
          }
          $_SESSION['return'][] = array(
            'type' => 'success',
            'log' => array(__FUNCTION__, $action),
            'msg' => 'Configuration updated'
          );
          return true;
        break;

        case 'preferences':
          // Update user preferences
          if (!isset($data['username'])) {
            $_SESSION['return'][] = array(
              'type' => 'danger',
              'log' => array(__FUNCTION__, $action),
              'msg' => 'Username required'
            );
            return false;
          }

          $stmt = $pdo->prepare("INSERT INTO `llm_user_preferences`
                                (`username`, `auto_analysis`, `auto_categorize`, `phishing_alerts`, `summary_enabled`)
                                VALUES (:username, :auto_analysis, :auto_categorize, :phishing_alerts, :summary_enabled)
                                ON DUPLICATE KEY UPDATE
                                `auto_analysis` = :auto_analysis,
                                `auto_categorize` = :auto_categorize,
                                `phishing_alerts` = :phishing_alerts,
                                `summary_enabled` = :summary_enabled");

          $stmt->execute(array(
            ':username' => $data['username'],
            ':auto_analysis' => isset($data['auto_analysis']) ? (int)$data['auto_analysis'] : 1,
            ':auto_categorize' => isset($data['auto_categorize']) ? (int)$data['auto_categorize'] : 1,
            ':phishing_alerts' => isset($data['phishing_alerts']) ? (int)$data['phishing_alerts'] : 1,
            ':summary_enabled' => isset($data['summary_enabled']) ? (int)$data['summary_enabled'] : 1
          ));

          $_SESSION['return'][] = array(
            'type' => 'success',
            'log' => array(__FUNCTION__, $action),
            'msg' => 'Preferences updated'
          );
          return true;
        break;
      }
    break;

    case 'delete':
      /**
       * Delete LLM analysis data
       */
      if (!isset($data['items']) || !is_array($data['items'])) {
        $_SESSION['return'][] = array(
          'type' => 'danger',
          'log' => array(__FUNCTION__, $action),
          'msg' => 'Items array required'
        );
        return false;
      }

      foreach ($data['items'] as $id) {
        $stmt = $pdo->prepare("DELETE FROM `llm_email_analysis` WHERE `id` = :id");
        $stmt->execute(array(':id' => $id));
      }

      $_SESSION['return'][] = array(
        'type' => 'success',
        'log' => array(__FUNCTION__, $action),
        'msg' => 'Analysis data deleted'
      );
      return true;
    break;

    default:
      $_SESSION['return'][] = array(
        'type' => 'danger',
        'log' => array(__FUNCTION__, $action),
        'msg' => 'Unknown action'
      );
      return false;
  }
}
