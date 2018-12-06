-- MySQL dump 10.13  Distrib 5.5.57, for debian-linux-gnu (x86_64)
--
-- Host: 0.0.0.0    Database: c9
-- ------------------------------------------------------
-- Server version	5.5.57-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `address_list`
--

DROP TABLE IF EXISTS `address_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `address_list` (
  `name` varchar(20) DEFAULT NULL,
  `kind` varchar(10) DEFAULT NULL,
  `city` varchar(20) DEFAULT NULL,
  `state` char(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `address_list`
--

LOCK TABLES `address_list` WRITE;
/*!40000 ALTER TABLE `address_list` DISABLE KEYS */;
INSERT INTO `address_list` VALUES ('Mom','home','Fairfax','VA'),('Connie','home','Lynden','WA'),('Dad','home','Charlotte','NC'),('Lynn','home','Los Angeles','CA'),('Pattie','home','Wellesley','MA'),('Allen','work','Needham','MA'),('Jeff','home','Wellesley','MA'),('Pat','home','Natick','MA'),('Matt Damon','home','Boston','MA'),('Matt Damon','home','Hollywood','CA'),('Scout','home','Dartmouth','NH'),('Ron','home','Portland','ME'),('Fred','home','New Haven','CT'),('George','home','Providence','RI'),('Harry','home','Montpelier','VT'),('Percy','work','Providence','RI');
/*!40000 ALTER TABLE `address_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `items` (
  `iid` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(100) DEFAULT NULL,
  `price` float NOT NULL,
  `availability` enum('yes','no') NOT NULL,
  `urgency` int(11) DEFAULT NULL,
  `category` set('food','clothing','shoes','services','utility','makeup','bath/body','event','other') NOT NULL,
  `other` varchar(30) DEFAULT NULL,
  `photo` blob,
  `role` enum('buyer','seller') NOT NULL,
  PRIMARY KEY (`iid`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES (1,'Ugly Ugg boots',50,'yes',3,'shoes',NULL,NULL,'seller'),(2,'Zara dress',35,'yes',NULL,'clothing',NULL,NULL,'seller'),(3,'Muji stationery',5,'yes',NULL,'other','stationery',NULL,'seller'),(4,'Peach palette',29,'yes',NULL,'makeup',NULL,NULL,'seller');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phone_list`
--

DROP TABLE IF EXISTS `phone_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `phone_list` (
  `name` varchar(20) DEFAULT NULL,
  `kind` varchar(20) DEFAULT NULL,
  `phnum` char(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `phone_list`
--

LOCK TABLES `phone_list` WRITE;
/*!40000 ALTER TABLE `phone_list` DISABLE KEYS */;
INSERT INTO `phone_list` VALUES ('Mom','home','7035555681'),('Mom','cell','7035551234'),('Connie','home','6095551243'),('Dad','home','7045553004'),('Dad','cell','7045551324'),('Dad','other','7045551343'),('Lynn','cell','6915551423'),('Pattie','home','6175551432'),('Allen','home','6175552134'),('Jeff','work','7815552314'),('Pat','work','7815552341'),('Matt Damon','work','6175552341'),('Scout','cell','8085553124'),('Ron','home','2075551111'),('Fred','cell','2035552222'),('George','work','4015553333'),('George','home','4015554444'),('Harry','home','8025558888'),('Percy','cell','4015559999');
/*!40000 ALTER TABLE `phone_list` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `posts` (
  `uid` int(11) NOT NULL,
  `iid` int(11) NOT NULL,
  PRIMARY KEY (`uid`,`iid`),
  KEY `uid` (`uid`),
  KEY `iid` (`iid`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`) ON DELETE CASCADE,
  CONSTRAINT `posts_ibfk_2` FOREIGN KEY (`iid`) REFERENCES `items` (`iid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
INSERT INTO `posts` VALUES (5,1),(6,2),(7,3),(7,4);
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `gradYear` int(11) NOT NULL,
  `dorm` varchar(20) NOT NULL,
  `email` varchar(50) NOT NULL,
  PRIMARY KEY (`uid`),
  KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'ssola','Sasha',2020,'McAfee Hall','sola@wellesley.edu'),(2,'mary','Mary',2019,'Freeman Hall','mlamb@wellesley.edu'),(3,'mary','Mary',2021,'Freeman Hall','mlamb@wellesley.edu'),(4,'janice','Janice',2021,'Bates Hall','jtan@wellesley.edu'),(5,'jane','Jane',2019,'Beebe Hall','janed@wellesley.edu'),(6,'wwellesley','Wendy',2020,'McAfee Hall','wwelles@wellesley.edu'),(7,'sstone','Sally',2021,'Freeman Hall','sstone@wellesley.edu'),(8,'happygirl','Denise',2019,'Stone Davis Hall','dlange@wellesley.edu'),(9,'Harrystyles','Crazy',2020,'Pomeroy Hall','hstyles@wellesley.edu');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `userpass`
--

DROP TABLE IF EXISTS `userpass`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `userpass` (
  `username` varchar(50) NOT NULL,
  `hashed` char(60) DEFAULT NULL,
  PRIMARY KEY (`username`),
  CONSTRAINT `userpass_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `userpass`
--

LOCK TABLES `userpass` WRITE;
/*!40000 ALTER TABLE `userpass` DISABLE KEYS */;
INSERT INTO `userpass` VALUES ('happygirl','$2b$12$0.1pJ41EYINNRcXHDy5Lre4hW96GrmTgz/xmqCbzVHKkUo62QAd9S'),('Harrystyles','$2b$12$XXyA4e1iQQ0l9oZfxv4peeqqzW.mG/P80mDm7Ia1VTpJSpD4PYgVy'),('jane','$2b$12$UdZesXPLJ400aSfo5n6p4.Am5JU6PezC5ygue/DIenHGAr/tux2lW'),('janice','$2b$12$zZPf/YUcLjhMZhTZmADz0./Ky2vzWdj.pyedxIf.4/w5pK2kQQAJa'),('mary','$2b$12$PAqTgmPtqnzHXmyT23xPkul9SnbjEDZtq.Pqd/vcTjFheMx4X8PKO'),('ssola','$2b$12$IIjmZjsuSK.ezTDc852KzOxhhYlr6fBCw2Ktji4Mps5BVht/EXM4G'),('sstone','$2b$12$.9ockGNw5wvYvVoN.PibaudAGoAcVBnV/67Lo.qXrxipwwsbIAmqu'),('wwellesley','$2b$12$ynpYuB32yZnqr/rVn5Sz9.H0XCl7XzAs68lH20P.l5oesqCTNIzbq');
/*!40000 ALTER TABLE `userpass` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-12-06  4:45:47
